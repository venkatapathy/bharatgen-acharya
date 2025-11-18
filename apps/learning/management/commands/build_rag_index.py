"""
Management command to build RAG index from learning content.
"""
from django.core.management.base import BaseCommand
from apps.rag.pipeline import get_rag_pipeline
from apps.recommendations.engine import get_recommendation_engine


class Command(BaseCommand):
    help = 'Build RAG index from learning content in database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing index before building',
        )
        parser.add_argument(
            '--compute-similarity',
            action='store_true',
            help='Compute similarity scores between learning paths',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Building RAG index...')
        
        rag_pipeline = get_rag_pipeline()
        
        # Clear existing index if requested
        if options['clear']:
            self.stdout.write('Clearing existing index...')
            rag_pipeline.clear_index()
        
        # Index content from database
        self.stdout.write('Indexing learning content...')
        try:
            ids = rag_pipeline.index_content_from_db()
            self.stdout.write(self.style.SUCCESS(f'Successfully indexed {len(ids)} document chunks'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error indexing content: {str(e)}'))
            return
        
        # Get stats
        stats = rag_pipeline.get_stats()
        self.stdout.write(f'RAG Stats:')
        self.stdout.write(f'  - Vector Store: {stats["vector_store"]["count"]} documents')
        self.stdout.write(f'  - Embedding Dimension: {stats["embedding_dimension"]}')
        self.stdout.write(f'  - LLM Model: {stats["llm_model"]}')
        
        # Compute similarity scores if requested
        if options['compute_similarity']:
            self.stdout.write('Computing similarity scores...')
            try:
                rec_engine = get_recommendation_engine()
                rec_engine.compute_similarity_scores()
                self.stdout.write(self.style.SUCCESS('Successfully computed similarity scores'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Warning: Could not compute similarities: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('RAG index built successfully!'))

