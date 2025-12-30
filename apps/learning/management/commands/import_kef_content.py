import csv
import os
import re
import docx
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.learning.models import LearningPath, Module, Content

User = get_user_model()

class Command(BaseCommand):
    help = 'Import KEF content from CSV and DOCX files'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, help='Path to CSV file')
        parser.add_argument('--docx', type=str, help='Path to DOCX file')

    def handle(self, *args, **options):
        # Default paths
        csv_path = options['csv'] or 'kefdata/CE-FR Year 1 (Bud) Sample Content - Sheet1.csv'
        docx_path = options['docx'] or 'kefdata/KEF - CE-FR Year 1 Pre Test-Post Test Paper.docx'

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        if not os.path.exists(docx_path):
            self.stdout.write(self.style.WARNING(f'DOCX file not found: {docx_path}. Skipping DOCX import.'))
            docx_path = None

        # Get or create admin user for attribution
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.WARNING('No users found. Creating content without owner.'))

        # 1. Import CSV Content
        self.import_csv(csv_path, user)

        # 2. Import DOCX Content
        if docx_path:
            self.import_docx(docx_path, user)

    def import_csv(self, csv_path, user):
        self.stdout.write(f'Importing CSV from {csv_path}...')
        
        # Create Learning Path
        lp_title = "CE-FR Year 1 (Bud)"
        lp, created = LearningPath.objects.get_or_create(
            title=lp_title,
            defaults={
                'slug': slugify(lp_title),
                'description': 'Communicative English Future Readiness Year 1 course.',
                'difficulty_level': 'beginner',
                'estimated_hours': 10,
                'is_published': True,
                'created_by': user
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Learning Path: {lp.title}'))
        else:
            self.stdout.write(f'Using existing Learning Path: {lp.title}')

        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Group by lesson (Module)
            # The CSV structure is flat, so we need to track current module
            
            # First pass: identify unique modules to ensure order
            # Actually, we can just get_or_create module as we go, but we need to manage 'order' field.
            
            module_orders = {} # title -> order
            content_orders = {} # module_id -> next_order
            
            current_module_order = 1
            
            for row in reader:
                lesson_name = row['Name of the lesson'].strip()
                if not lesson_name:
                    continue
                    
                # Create/Get Module
                module, m_created = Module.objects.get_or_create(
                    learning_path=lp,
                    title=lesson_name,
                    defaults={
                        'description': f"Lessons for {lesson_name}",
                        'order': current_module_order,
                        'estimated_minutes': 30 # Default
                    }
                )
                
                if m_created:
                    self.stdout.write(self.style.SUCCESS(f'  Created Module: {lesson_name}'))
                    current_module_order += 1
                
                # Content creation
                content_title = row['Modules and its title'].strip()
                video_url = row['Link for the Content'].strip()
                duration_str = row['Video duration'].strip()
                
                # Parse duration (e.g., "3:46")
                minutes = 5
                try:
                    if ':' in duration_str:
                        parts = duration_str.split(':')
                        minutes = int(parts[0]) + (1 if int(parts[1]) > 0 else 0)
                    else:
                        minutes = int(duration_str)
                except:
                    pass

                # Calculate content order
                if module.id not in content_orders:
                    content_orders[module.id] = 1
                order = content_orders[module.id]
                
                content, c_created = Content.objects.get_or_create(
                    module=module,
                    title=content_title,
                    defaults={
                        'content_type': 'video',
                        'video_url': video_url,
                        'order': order,
                        'estimated_minutes': minutes,
                        'metadata': {'duration_raw': duration_str}
                    }
                )
                
                if c_created:
                    self.stdout.write(f'    Added Content: {content_title}')
                
                content_orders[module.id] += 1

    def import_docx(self, docx_path, user):
        self.stdout.write(f'Importing DOCX from {docx_path}...')
        
        # Find the Learning Path
        lp = LearningPath.objects.get(title="CE-FR Year 1 (Bud)")
        
        # Create Assessment Module
        module, _ = Module.objects.get_or_create(
            learning_path=lp,
            title="Assessment - Pre/Post Test",
            defaults={
                'description': "Practice sessions and assessments.",
                'order': 999, # Put at the end
                'estimated_minutes': 60
            }
        )
        
        # Parse DOCX
        doc = docx.Document(docx_path)
        
        full_text = []
        questions = []
        
        current_question = None
        
        # Heuristic parsing
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            full_text.append(text)
            
            # Check for question start
            # Pattern: "Question 1:", "Q1.", etc.
            if re.match(r'^Question\s+\d+[:.]', text, re.IGNORECASE):
                if current_question:
                    questions.append(current_question)
                
                current_question = {
                    'id': len(questions) + 1,
                    'question': text,
                    'reference_answer': "", # Open ended mostly
                    'type': 'descriptive'
                }
            elif current_question:
                # Append to current question description
                current_question['question'] += "\n" + text
            
            # Add placeholders for missing assets
            if "audio" in text.lower() or "listen" in text.lower():
                 if "[**MISSING AUDIO**]" not in text:
                     full_text.append(f"   [**MISSING AUDIO: Please upload audio file for this section**]")
            if "image" in text.lower() or "picture" in text.lower():
                 if "[**MISSING IMAGE**]" not in text:
                     full_text.append(f"   [**MISSING IMAGE: Please upload image file for this section**]")
        
        # Add last question
        if current_question:
            questions.append(current_question)
            
        # Add placeholders for missing assets
        processed_text = "\n\n".join(full_text)
        
        # Create Content Item
        content, c_created = Content.objects.get_or_create(
            module=module,
            title="Year 1 Pre-Test Paper",
            defaults={
                'content_type': 'text',
                'order': 1,
                'text_content': processed_text,
                'questions': {'items': questions},
                'estimated_minutes': 45,
                'metadata': {
                    'source_file': os.path.basename(docx_path),
                    'notes': 'Contains placeholders for audio/images.'
                }
            }
        )
        
        if c_created:
            self.stdout.write(self.style.SUCCESS(f'  Created Assessment Content with {len(questions)} questions extracted.'))
        else:
            # Update existing
            content.text_content = processed_text
            content.questions = {'items': questions}
            content.save()
            self.stdout.write(f'  Updated Assessment Content: {len(questions)} questions.')


