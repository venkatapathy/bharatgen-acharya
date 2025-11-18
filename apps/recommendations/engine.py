"""
Recommendation engine with collaborative and content-based filtering.
"""
from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from apps.learning.models import LearningPath, Content, UserProgress
from apps.rag.pipeline import get_rag_pipeline
from .models import Recommendation, UserInteraction, SimilarityScore
import numpy as np
from collections import defaultdict


class RecommendationEngine:
    """Hybrid recommendation engine."""
    
    def __init__(self):
        self.rag_pipeline = get_rag_pipeline()
    
    def get_recommendations(
        self,
        user: User,
        recommendation_type: str = None,
        limit: int = 10
    ) -> List[Recommendation]:
        """
        Get personalized recommendations for a user.
        
        Args:
            user: Django user
            recommendation_type: Optional type filter
            limit: Maximum number of recommendations
            
        Returns:
            List of Recommendation objects
        """
        recommendations = []
        
        if recommendation_type is None or recommendation_type == 'next_content':
            recommendations.extend(self._get_next_content_recommendations(user, limit=3))
        
        if recommendation_type is None or recommendation_type == 'similar_path':
            recommendations.extend(self._get_similar_path_recommendations(user, limit=3))
        
        if recommendation_type is None or recommendation_type == 'collaborative':
            recommendations.extend(self._get_collaborative_recommendations(user, limit=3))
        
        if recommendation_type is None or recommendation_type == 'skill_gap':
            recommendations.extend(self._get_skill_gap_recommendations(user, limit=2))
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def _get_next_content_recommendations(self, user: User, limit: int = 3) -> List[Recommendation]:
        """Recommend next logical content based on current progress."""
        recommendations = []
        
        # Find in-progress learning paths
        in_progress = UserProgress.objects.filter(
            user=user,
            status='in_progress',
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True
        ).select_related('learning_path')
        
        for progress in in_progress[:limit]:
            # Find next incomplete module
            completed_modules = UserProgress.objects.filter(
                user=user,
                learning_path=progress.learning_path,
                module__isnull=False,
                content__isnull=True,
                status='completed'
            ).values_list('module_id', flat=True)
            
            next_module = progress.learning_path.modules.exclude(
                id__in=completed_modules
            ).order_by('order').first()
            
            if next_module:
                # Find first incomplete content in module
                completed_contents = UserProgress.objects.filter(
                    user=user,
                    module=next_module,
                    content__isnull=False,
                    status='completed'
                ).values_list('content_id', flat=True)
                
                next_content = next_module.contents.exclude(
                    id__in=completed_contents
                ).order_by('order').first()
                
                if next_content:
                    recommendation = Recommendation(
                        user=user,
                        recommendation_type='next_content',
                        learning_path=progress.learning_path,
                        content=next_content,
                        score=1.0,
                        reasoning=f"Continue your learning journey in {progress.learning_path.title}"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _get_similar_path_recommendations(self, user: User, limit: int = 3) -> List[Recommendation]:
        """Recommend similar learning paths based on completed/in-progress paths."""
        recommendations = []
        
        # Get user's learning paths
        user_paths = UserProgress.objects.filter(
            user=user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True
        ).values_list('learning_path_id', flat=True)
        
        if not user_paths:
            return recommendations
        
        # Find similar paths using precomputed similarity scores
        similar_paths = SimilarityScore.objects.filter(
            learning_path_1_id__in=user_paths
        ).exclude(
            learning_path_2_id__in=user_paths
        ).order_by('-similarity_score')[:limit]
        
        for similarity in similar_paths:
            recommendation = Recommendation(
                user=user,
                recommendation_type='similar_path',
                learning_path=similarity.learning_path_2,
                score=similarity.similarity_score,
                reasoning=f"Similar to {similarity.learning_path_1.title} which you're learning"
            )
            recommendations.append(recommendation)
        
        # If no precomputed scores, use tag-based similarity
        if not recommendations:
            for path_id in user_paths:
                try:
                    path = LearningPath.objects.get(id=path_id)
                    similar = self._find_similar_by_tags(path, exclude_ids=user_paths, limit=limit)
                    recommendations.extend(similar)
                except LearningPath.DoesNotExist:
                    continue
        
        return recommendations[:limit]
    
    def _find_similar_by_tags(
        self,
        learning_path: LearningPath,
        exclude_ids: List[int],
        limit: int = 3
    ) -> List[Recommendation]:
        """Find similar paths by matching tags."""
        recommendations = []
        
        if not learning_path.tags:
            return recommendations
        
        similar_paths = LearningPath.objects.filter(
            is_published=True
        ).exclude(
            id__in=exclude_ids
        )
        
        # Score by tag overlap
        scored_paths = []
        for path in similar_paths:
            if not path.tags:
                continue
            
            overlap = len(set(learning_path.tags) & set(path.tags))
            if overlap > 0:
                score = overlap / max(len(learning_path.tags), len(path.tags))
                scored_paths.append((path, score))
        
        # Sort by score
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        
        for path, score in scored_paths[:limit]:
            recommendation = Recommendation(
                user=learning_path.id,  # Placeholder
                recommendation_type='similar_path',
                learning_path=path,
                score=score,
                reasoning=f"Shares {len(set(learning_path.tags) & set(path.tags))} topics with {learning_path.title}"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_collaborative_recommendations(self, user: User, limit: int = 3) -> List[Recommendation]:
        """Recommend based on what similar users learned (collaborative filtering)."""
        recommendations = []
        
        # Get user's completed paths
        user_paths = UserProgress.objects.filter(
            user=user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True,
            status__in=['in_progress', 'completed']
        ).values_list('learning_path_id', flat=True)
        
        if not user_paths:
            return recommendations
        
        # Find users with similar learning patterns
        similar_users = UserProgress.objects.filter(
            learning_path_id__in=user_paths
        ).exclude(
            user=user
        ).values('user').annotate(
            overlap=Count('learning_path_id')
        ).order_by('-overlap')[:20]
        
        similar_user_ids = [u['user'] for u in similar_users]
        
        # Find what these users also learned
        other_paths = UserProgress.objects.filter(
            user_id__in=similar_user_ids,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True
        ).exclude(
            learning_path_id__in=user_paths
        ).values('learning_path').annotate(
            popularity=Count('user'),
            avg_progress=Avg('progress_percentage')
        ).order_by('-popularity')[:limit]
        
        for item in other_paths:
            try:
                path = LearningPath.objects.get(id=item['learning_path'], is_published=True)
                score = min(item['popularity'] / len(similar_user_ids), 1.0)
                
                recommendation = Recommendation(
                    user=user,
                    recommendation_type='collaborative',
                    learning_path=path,
                    score=score,
                    reasoning=f"{item['popularity']} similar learners also studied this"
                )
                recommendations.append(recommendation)
            except LearningPath.DoesNotExist:
                continue
        
        return recommendations
    
    def _get_skill_gap_recommendations(self, user: User, limit: int = 2) -> List[Recommendation]:
        """Recommend content to fill knowledge gaps."""
        recommendations = []
        
        # Find user's learning preferences and level
        try:
            profile = user.profile
            interests = profile.interests or []
            level = profile.learning_level
        except:
            return recommendations
        
        # Find paths matching interests but not yet started
        enrolled_paths = UserProgress.objects.filter(
            user=user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True
        ).values_list('learning_path_id', flat=True)
        
        for interest in interests[:3]:  # Check top 3 interests
            paths = LearningPath.objects.filter(
                tags__contains=[interest],
                difficulty_level=level,
                is_published=True
            ).exclude(
                id__in=enrolled_paths
            ).order_by('-total_enrollments')[:limit]
            
            for path in paths:
                recommendation = Recommendation(
                    user=user,
                    recommendation_type='skill_gap',
                    learning_path=path,
                    score=0.8,
                    reasoning=f"Matches your interest in {interest} at {level} level"
                )
                recommendations.append(recommendation)
        
        return recommendations[:limit]
    
    def compute_similarity_scores(self, batch_size: int = 50):
        """
        Compute and store similarity scores between learning paths.
        Uses embedding-based similarity.
        
        Args:
            batch_size: Batch size for processing
        """
        paths = LearningPath.objects.filter(is_published=True)
        
        # Get embeddings for all paths
        path_embeddings = {}
        
        for path in paths:
            # Create text representation
            text = f"{path.title}. {path.description}. Tags: {', '.join(path.tags or [])}"
            embedding = self.rag_pipeline.embedding.embed_text(text)
            path_embeddings[path.id] = np.array(embedding)
        
        # Compute pairwise similarities
        path_ids = list(path_embeddings.keys())
        
        for i, path_id_1 in enumerate(path_ids):
            for path_id_2 in path_ids[i+1:]:
                emb1 = path_embeddings[path_id_1]
                emb2 = path_embeddings[path_id_2]
                
                # Cosine similarity
                similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                
                # Store if significant
                if similarity > 0.5:
                    SimilarityScore.objects.update_or_create(
                        learning_path_1_id=path_id_1,
                        learning_path_2_id=path_id_2,
                        score_type='embedding',
                        defaults={'similarity_score': float(similarity)}
                    )
        
        print(f"Computed similarity scores for {len(path_ids)} learning paths")
    
    def track_interaction(
        self,
        user: User,
        interaction_type: str,
        learning_path: Optional[LearningPath] = None,
        content: Optional[Content] = None,
        **kwargs
    ):
        """
        Track user interaction for recommendation engine.
        
        Args:
            user: Django user
            interaction_type: Type of interaction
            learning_path: Optional learning path
            content: Optional content
            **kwargs: Additional interaction data
        """
        UserInteraction.objects.create(
            user=user,
            interaction_type=interaction_type,
            learning_path=learning_path,
            content=content,
            duration_seconds=kwargs.get('duration_seconds'),
            completion_percentage=kwargs.get('completion_percentage'),
            rating=kwargs.get('rating'),
            session_id=kwargs.get('session_id'),
            referrer=kwargs.get('referrer')
        )


# Singleton instance
_recommendation_engine = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get or create the recommendation engine singleton."""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine

