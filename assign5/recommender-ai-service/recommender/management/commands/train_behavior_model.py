"""Management command to train behavior model"""
from django.core.management.base import BaseCommand
from recommender.behavior_model.train import train_behavior_model
from recommender.rag.kb_builder import build_kb


class Command(BaseCommand):
    help = 'Train the behavior model and build knowledge base'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model-only',
            action='store_true',
            help='Train only the behavior model, skip KB building',
        )
        parser.add_argument(
            '--kb-only',
            action='store_true',
            help='Build only the knowledge base, skip model training',
        )
    
    def handle(self, *args, **options):
        model_only = options.get('model_only', False)
        kb_only = options.get('kb_only', False)
        
        if kb_only:
            self.stdout.write(self.style.WARNING('Building knowledge base...'))
            try:
                success = build_kb()
                if success:
                    self.stdout.write(self.style.SUCCESS('✓ Knowledge base built successfully'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Failed to build knowledge base'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))
        
        elif model_only:
            self.stdout.write(self.style.WARNING('Training behavior model...'))
            try:
                success = train_behavior_model()
                if success:
                    self.stdout.write(self.style.SUCCESS('✓ Behavior model trained successfully'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Failed to train behavior model'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))
        
        else:
            # Train everything
            self.stdout.write(self.style.WARNING('Training behavior model and building knowledge base...'))
            
            try:
                # Train behavior model
                self.stdout.write('Step 1/2: Training behavior model...')
                success_model = train_behavior_model()
                
                if success_model:
                    self.stdout.write(self.style.SUCCESS('✓ Behavior model trained'))
                else:
                    self.stdout.write(self.style.WARNING('✗ Behavior model training had issues'))
                
                # Build KB
                self.stdout.write('Step 2/2: Building knowledge base...')
                success_kb = build_kb()
                
                if success_kb:
                    self.stdout.write(self.style.SUCCESS('✓ Knowledge base built'))
                else:
                    self.stdout.write(self.style.WARNING('✗ Knowledge base building had issues'))
                
                if success_model and success_kb:
                    self.stdout.write(self.style.SUCCESS('\n✓✓✓ All training completed successfully! ✓✓✓'))
                else:
                    self.stdout.write(self.style.WARNING('\n⚠ Some training steps failed, please check logs'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))
