"""
Relevance scoring module for ranking document sections based on persona and job queries.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Scores document sections for relevance to persona and job requirements."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize the relevance scorer.
        
        Args:
            model_path: Optional path to pre-trained sentence transformer model
        """
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # Try to use sentence transformers if available and model is small enough
        self.sentence_model = None
        self._init_sentence_model(model_path)
        
        self.fitted = False
        
    def _init_sentence_model(self, model_path: str = None):
        """Initialize sentence transformer model if available."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a small, efficient model that's under 1GB
            model_name = model_path or 'all-MiniLM-L6-v2'  # ~90MB model
            
            # Check if model exists locally or download
            try:
                self.sentence_model = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
                self.sentence_model = None
                
        except ImportError:
            logger.warning("SentenceTransformers not available, using TF-IDF only")
            self.sentence_model = None
    
    def fit_corpus(self, documents: List[Dict[str, Any]]):
        """
        Fit the TF-IDF vectorizer on the document corpus.
        
        Args:
            documents: List of document data dictionaries
        """
        all_texts = []
        
        for doc in documents:
            for page in doc['pages']:
                # Add page text
                if page['cleaned_text']:
                    all_texts.append(page['cleaned_text'])
                
                # Add section texts
                for section in page['sections']:
                    if section['content']:
                        all_texts.append(section['content'])
        
        if all_texts:
            try:
                self.tfidf_vectorizer.fit(all_texts)
                self.fitted = True
                logger.info(f"TF-IDF vectorizer fitted on {len(all_texts)} text segments")
            except Exception as e:
                logger.error(f"Error fitting TF-IDF vectorizer: {e}")
                raise
        else:
            logger.warning("No text found to fit TF-IDF vectorizer")
    
    def score_sections(self, doc_data: Dict[str, Any], query_text: str) -> List[Dict[str, Any]]:
        """
        Score and rank document sections based on relevance to query.
        
        Args:
            doc_data: Document data dictionary
            query_text: Combined persona and job text
            
        Returns:
            List of scored sections sorted by relevance
        """
        sections_with_scores = []
        
        for page in doc_data['pages']:
            for section in page['sections']:
                if not section['content']:
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance_score(section['content'], query_text)
                
                sections_with_scores.append({
                    'document': doc_data['document'],
                    'page': section['page'],
                    'section_title': section['title'],
                    'content': section['content'],
                    'word_count': section['word_count'],
                    'relevance_score': score
                })
        
        # Sort by relevance score (descending) and assign importance ranks
        sections_with_scores.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Assign importance ranks
        ranked_sections = []
        for rank, section in enumerate(sections_with_scores[:20], 1):  # Top 20 sections
            ranked_sections.append({
                'document': section['document'],
                'page': section['page'],
                'section_title': section['section_title'],
                'importance_rank': rank
            })
        
        return ranked_sections
    
    def score_subsections(self, doc_data: Dict[str, Any], query_text: str) -> List[Dict[str, Any]]:
        """
        Score and rank document subsections with refined text.
        
        Args:
            doc_data: Document data dictionary
            query_text: Combined persona and job text
            
        Returns:
            List of scored subsections with refined text
        """
        subsections_with_scores = []
        
        for page in doc_data['pages']:
            if not page['cleaned_text']:
                continue
            
            # Split page text into paragraphs for subsection analysis
            paragraphs = [p.strip() for p in page['cleaned_text'].split('\n') if p.strip()]
            
            for para in paragraphs:
                if len(para.split()) < 20:  # Skip very short paragraphs
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance_score(para, query_text)
                
                # Refine text (extract most relevant sentences)
                refined_text = self._refine_text(para, query_text)
                
                if refined_text:
                    subsections_with_scores.append({
                        'document': doc_data['document'],
                        'page': page['page_number'],
                        'original_text': para,
                        'refined_text': refined_text,
                        'relevance_score': score
                    })
        
        # Sort by relevance score and assign importance ranks
        subsections_with_scores.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        ranked_subsections = []
        for rank, subsection in enumerate(subsections_with_scores[:15], 1):  # Top 15 subsections
            ranked_subsections.append({
                'document': subsection['document'],
                'page': subsection['page'],
                'refined_text': subsection['refined_text'],
                'importance_rank': rank
            })
        
        return ranked_subsections
    
    def _calculate_relevance_score(self, text: str, query_text: str) -> float:
        """
        Calculate relevance score between text and query.
        
        Args:
            text: Text to score
            query_text: Query text (persona + job)
            
        Returns:
            Relevance score between 0 and 1
        """
        if not text or not query_text:
            return 0.0
        
        # Use sentence transformers if available
        if self.sentence_model:
            try:
                text_embedding = self.sentence_model.encode([text])
                query_embedding = self.sentence_model.encode([query_text])
                similarity = cosine_similarity(text_embedding, query_embedding)[0][0]
                return float(similarity)
            except Exception as e:
                logger.warning(f"Error using sentence model: {e}")
        
        # Fallback to TF-IDF
        try:
            if not self.fitted:
                # Quick fit on current texts
                self.tfidf_vectorizer.fit([text, query_text])
                self.fitted = True
            
            text_vector = self.tfidf_vectorizer.transform([text])
            query_vector = self.tfidf_vectorizer.transform([query_text])
            similarity = cosine_similarity(text_vector, query_vector)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Error calculating TF-IDF similarity: {e}")
            return self._simple_keyword_similarity(text, query_text)
    
    def _simple_keyword_similarity(self, text: str, query_text: str) -> float:
        """Simple keyword-based similarity as final fallback."""
        text_words = set(text.lower().split())
        query_words = set(query_text.lower().split())
        
        if not text_words or not query_words:
            return 0.0
        
        intersection = text_words.intersection(query_words)
        union = text_words.union(query_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _refine_text(self, text: str, query_text: str, max_sentences: int = 3) -> str:
        """
        Refine text by extracting most relevant sentences.
        
        Args:
            text: Original text
            query_text: Query text for relevance scoring
            max_sentences: Maximum number of sentences to include
            
        Returns:
            Refined text with most relevant sentences
        """
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # Score each sentence
        sentence_scores = []
        for sentence in sentences:
            if len(sentence.split()) >= 5:  # Only consider substantial sentences
                score = self._calculate_relevance_score(sentence, query_text)
                sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in sentence_scores[:max_sentences]]
        
        # Reconstruct text maintaining original order
        refined_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                refined_sentences.append(sentence)
        
        return '. '.join(refined_sentences) + '.' if refined_sentences else text[:500]
