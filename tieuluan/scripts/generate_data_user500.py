"""Generate synthetic user behavior dataset for sequence-model training.

Output CSV columns:
    user_id, product_id, action, timestamp

Behavior types:
    view, click, search, add_to_cart, update_quantity,
    remove_cart, purchase, rate
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


BEHAVIORS: Tuple[str, ...] = (
    "view",
    "click",
    "search",
    "add_to_cart",
    "update_quantity",
    "remove_cart",
    "purchase",
    "rate",
)


BASE_WEIGHTS: Dict[str, float] = {
    "view": 0.28,
    "click": 0.18,
    "search": 0.18,
    "add_to_cart": 0.14,
    "update_quantity": 0.07,
    "remove_cart": 0.05,
    "purchase": 0.07,
    "rate": 0.03,
}


@dataclass
class Event:
    user_id: int
    product_id: int
    action: str
    timestamp: datetime


def weighted_choice(items: Sequence[str], weights: Sequence[float], rng: random.Random) -> str:
    total = sum(weights)
    roll = rng.random() * total
    upto = 0.0
    for item, weight in zip(items, weights):
        upto += weight
        if roll <= upto:
            return item
    return items[-1]


def choose_action(
    rng: random.Random,
    prev_action: str | None,
    cart: Dict[int, int],
    purchased: set[int],
    rated: set[int],
) -> str:
    weights = dict(BASE_WEIGHTS)

    if prev_action == "search":
        weights["view"] += 0.08
        weights["click"] += 0.05
    elif prev_action == "view":
        weights["click"] += 0.06
        weights["add_to_cart"] += 0.04
    elif prev_action == "add_to_cart":
        weights["update_quantity"] += 0.05
        weights["purchase"] += 0.04
    elif prev_action == "purchase":
        weights["rate"] += 0.12

    valid_actions: List[str] = ["view", "click", "search", "add_to_cart"]

    if cart:
        valid_actions.extend(["update_quantity", "remove_cart", "purchase"])

    if purchased - rated:
        valid_actions.append("rate")

    action_weights = [weights[a] for a in valid_actions]
    return weighted_choice(valid_actions, action_weights, rng)


def pick_product_for_action(
    action: str,
    rng: random.Random,
    product_ids: Sequence[int],
    recent_products: List[int],
    cart: Dict[int, int],
    purchased: set[int],
    rated: set[int],
) -> int:
    if action in {"update_quantity", "remove_cart", "purchase"} and cart:
        return rng.choice(list(cart.keys()))

    if action == "rate" and purchased - rated:
        return rng.choice(list(purchased - rated))

    if action in {"view", "click", "add_to_cart"} and recent_products and rng.random() < 0.6:
        return rng.choice(recent_products[-8:])

    return rng.choice(product_ids)


def apply_action_state(action: str, product_id: int, rng: random.Random, cart: Dict[int, int], purchased: set[int], rated: set[int]) -> None:
    if action == "add_to_cart":
        cart[product_id] = cart.get(product_id, 0) + 1
    elif action == "update_quantity" and product_id in cart:
        delta = rng.choice([-1, 1, 1])
        new_qty = max(1, cart[product_id] + delta)
        cart[product_id] = new_qty
    elif action == "remove_cart":
        cart.pop(product_id, None)
    elif action == "purchase":
        if product_id in cart:
            purchased.add(product_id)
            cart.pop(product_id, None)
    elif action == "rate":
        if product_id in purchased:
            rated.add(product_id)


def generate_events_for_user(
    user_id: int,
    rng: random.Random,
    product_ids: Sequence[int],
    min_events: int,
    max_events: int,
) -> List[Event]:
    num_events = rng.randint(min_events, max_events)
    now = datetime.now()
    start_ts = now - timedelta(days=rng.randint(40, 180), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))

    events: List[Event] = []
    recent_products: List[int] = []
    cart: Dict[int, int] = {}
    purchased: set[int] = set()
    rated: set[int] = set()
    prev_action: str | None = None
    current_ts = start_ts

    for _ in range(num_events):
        action = choose_action(rng, prev_action, cart, purchased, rated)
        product_id = pick_product_for_action(action, rng, product_ids, recent_products, cart, purchased, rated)

        current_ts += timedelta(minutes=rng.randint(2, 180), seconds=rng.randint(0, 59))
        event = Event(user_id=user_id, product_id=product_id, action=action, timestamp=current_ts)
        events.append(event)

        recent_products.append(product_id)
        apply_action_state(action, product_id, rng, cart, purchased, rated)
        prev_action = action

    return events


def ensure_all_behaviors(
    events: List[Event],
    rng: random.Random,
    product_ids: Sequence[int],
    users_count: int,
) -> None:
    existing = {e.action for e in events}
    missing = [b for b in BEHAVIORS if b not in existing]
    if not missing:
        return

    base_time = min(e.timestamp for e in events) if events else datetime.now()
    for idx, action in enumerate(missing):
        user_id = rng.randint(1, users_count)
        events.append(
            Event(
                user_id=user_id,
                product_id=rng.choice(product_ids),
                action=action,
                timestamp=base_time + timedelta(seconds=idx + 1),
            )
        )


def write_csv(path: Path, events: Sequence[Event]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "product_id", "action", "timestamp"])
        for e in events:
            writer.writerow([e.user_id, e.product_id, e.action, e.timestamp.strftime("%Y-%m-%d %H:%M:%S")])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate data_user500.csv for sequence modeling")
    parser.add_argument("--output", default="data_user500.csv", help="Output CSV path")
    parser.add_argument("--users", type=int, default=500, help="Number of users")
    parser.add_argument("--products", type=int, default=300, help="Number of product IDs (1..N)")
    parser.add_argument("--min-events", type=int, default=35, help="Minimum events per user")
    parser.add_argument("--max-events", type=int, default=80, help="Maximum events per user")
    parser.add_argument("--seed", type=int, default=20260419, help="Random seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.users <= 0:
        raise ValueError("--users must be > 0")
    if args.products <= 0:
        raise ValueError("--products must be > 0")
    if args.min_events <= 0 or args.max_events <= 0:
        raise ValueError("--min-events and --max-events must be > 0")
    if args.min_events > args.max_events:
        raise ValueError("--min-events cannot be greater than --max-events")

    rng = random.Random(args.seed)
    product_ids = list(range(1, args.products + 1))

    all_events: List[Event] = []
    for user_id in range(1, args.users + 1):
        user_rng = random.Random(args.seed + user_id * 9973)
        all_events.extend(
            generate_events_for_user(
                user_id=user_id,
                rng=user_rng,
                product_ids=product_ids,
                min_events=args.min_events,
                max_events=args.max_events,
            )
        )

    ensure_all_behaviors(all_events, rng, product_ids, args.users)
    all_events.sort(key=lambda e: (e.user_id, e.timestamp))

    output_path = Path(args.output).resolve()
    write_csv(output_path, all_events)

    action_counts = Counter(e.action for e in all_events)
    unique_users = len({e.user_id for e in all_events})
    unique_products = len({e.product_id for e in all_events})

    print(f"Saved: {output_path}")
    print(f"Rows: {len(all_events)}")
    print(f"Users: {unique_users}")
    print(f"Products: {unique_products}")
    print("Action distribution:")
    for action in BEHAVIORS:
        print(f"  - {action}: {action_counts.get(action, 0)}")


if __name__ == "__main__":
    main()
