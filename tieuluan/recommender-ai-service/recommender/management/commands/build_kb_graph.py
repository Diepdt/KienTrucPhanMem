import os
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from recommender.assignment.neo4j_kb_graph import Neo4jKBGraphService


class Command(BaseCommand):
    help = "Build Neo4j KB_Graph from CSV dataset or BehaviorEvent table"

    def add_arguments(self, parser):
        parser.add_argument("--data", default="", help="CSV path; if empty use BehaviorEvent table")
        parser.add_argument("--neo4j-uri", default=os.getenv("NEO4J_URI", ""))
        parser.add_argument("--neo4j-user", default=os.getenv("NEO4J_USER", ""))
        parser.add_argument("--neo4j-password", default=os.getenv("NEO4J_PASSWORD", ""))
        parser.add_argument("--wait-retries", type=int, default=30, help="Neo4j readiness retries")
        parser.add_argument("--wait-delay", type=float, default=1.5, help="Delay seconds between readiness retries")
        parser.add_argument("--batch-size", type=int, default=2000, help="Rows per Neo4j write batch")
        parser.add_argument("--write-retries", type=int, default=3, help="Retry attempts for write operations")
        parser.add_argument("--reset", action="store_true", help="Clear existing graph before importing")
        parser.add_argument(
            "--report",
            default="recommender/assignment/artifacts/kb_graph_report.json",
            help="Path to save KB graph report JSON",
        )

    def handle(self, *args, **options):
        service = Neo4jKBGraphService(
            uri=options["neo4j_uri"],
            username=options["neo4j_user"],
            password=options["neo4j_password"],
        )

        service.wait_until_ready(retries=options["wait_retries"], delay_seconds=options["wait_delay"])

        if options["reset"]:
            service.clear_graph()

        csv_path = options["data"].strip()
        if csv_path:
            path = Path(csv_path)
            if not path.exists():
                raise CommandError(f"CSV not found: {path}")
            result = service.ingest_csv(path, batch_size=options["batch_size"], retries=options["write_retries"])
        else:
            result = service.ingest_behavior_events(batch_size=options["batch_size"], retries=options["write_retries"])

        overview = service.graph_overview()
        report_path = Path(options["report"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "import_result": result,
            "overview": overview,
            "data_source": csv_path if csv_path else "BehaviorEvent table",
        }
        report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS("Neo4j KB_Graph build completed."))
        self.stdout.write(str(result))
        self.stdout.write(f"report: {report_path}")
