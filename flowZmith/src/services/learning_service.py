from sqlalchemy.orm import Session
from src.models.learning import Documentation, LearningInsight, DeploymentLog
from src.models.database import get_db
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LearningService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

    async def search_documentation(
        self,
        db: Session,
        query: str,
        limit: int = 10,
        use_semantic_search: bool = True
    ) -> List[Dict[str, Any]]:
        """Search documentation using TF-IDF or semantic search"""
        docs = db.query(Documentation).all()

        if not docs:
            return []

        if use_semantic_search:
            # Use TF-IDF vectorization for semantic search
            doc_texts = [doc.content for doc in docs]
            query_vector = self.vectorizer.fit_transform([query])
            doc_vectors = self.vectorizer.transform(doc_texts)

            similarities = cosine_similarity(query_vector, doc_vectors)[0]
            ranked_indices = np.argsort(similarities)[::-1]

            results = []
            for idx in ranked_indices[:limit]:
                if similarities[idx] > 0.1:  # Threshold for relevance
                    doc = docs[idx]
                    results.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                        "category": doc.category,
                        "tags": doc.tags,
                        "relevance_score": float(similarities[idx])
                    })
            return results
        else:
            # Simple keyword search
            query_lower = query.lower()
            results = []
            for doc in docs:
                if query_lower in doc.content.lower() or query_lower in doc.title.lower():
                    results.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                        "category": doc.category,
                        "tags": doc.tags,
                        "relevance_score": 1.0
                    })

            return results[:limit]

    def add_documentation(
        self,
        db: Session,
        title: str,
        content: str,
        source_url: str = None,
        category: str = None,
        tags: List[str] = None
    ) -> Documentation:
        """Add new documentation to the knowledge base"""
        doc = Documentation(
            title=title,
            content=content,
            source_url=source_url,
            category=category,
            tags=tags or []
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def log_deployment_insight(
        self,
        db: Session,
        user_id: int,
        deployment_id: int,
        insight_type: str,
        insight_data: Dict[str, Any],
        confidence_score: float = None
    ) -> LearningInsight:
        """Log learning insights from deployments"""
        insight = LearningInsight(
            user_id=user_id,
            insight_type=insight_type,
            insight_data=insight_data,
            confidence_score=confidence_score
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight

    def get_documentation_stats(self, db: Session) -> Dict[str, Any]:
        """Get documentation statistics"""
        total_docs = db.query(Documentation).count()
        categories = db.query(Documentation.category).distinct().all()
        category_counts = {}

        for category in categories:
            if category[0]:
                count = db.query(Documentation).filter(Documentation.category == category[0]).count()
                category_counts[category[0]] = count

        return {
            "total_documents": total_docs,
            "categories": category_counts,
            "average_document_length": self._get_average_doc_length(db)
        }

    def _get_average_doc_length(self, db: Session) -> float:
        """Calculate average document length"""
        docs = db.query(Documentation).all()
        if not docs:
            return 0
        total_length = sum(len(doc.content) for doc in docs)
        return total_length / len(docs)

    def get_user_insights(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get learning insights for a specific user"""
        insights = db.query(LearningInsight).filter(LearningInsight.user_id == user_id).all()
        return [
            {
                "id": insight.id,
                "insight_type": insight.insight_type,
                "insight_data": insight.insight_data,
                "confidence_score": insight.confidence_score,
                "created_at": insight.created_at.isoformat()
            }
            for insight in insights
        ]