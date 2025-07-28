"""
Text analysis module for processing and segmenting document text.
"""

import logging
import re
from typing import Dict, List, Any, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Handles text analysis, tokenization, and preprocessing."""
    
    def __init__(self):
        """Initialize the text analyzer."""
        self.stemmer = PorterStemmer()
        self._download_nltk_data()
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            logger.warning("NLTK stopwords not available, using basic set")
            self.stop_words = set([
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
                'through', 'during', 'before', 'after', 'above', 'below',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'this', 'that',
                'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our',
                'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
                'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
                'their', 'theirs', 'themselves'
            ])
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """
        Preprocess text for analysis.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Dictionary containing processed text components
        """
        if not text:
            return {
                'original': '',
                'cleaned': '',
                'sentences': [],
                'tokens': [],
                'filtered_tokens': [],
                'stemmed_tokens': []
            }
        
        # Clean text
        cleaned = self._clean_text(text)
        
        # Tokenize into sentences
        try:
            sentences = sent_tokenize(cleaned)
        except:
            # Fallback sentence splitting
            sentences = [s.strip() for s in cleaned.split('.') if s.strip()]
        
        # Tokenize into words
        try:
            tokens = word_tokenize(cleaned.lower())
        except:
            # Fallback word tokenization
            tokens = re.findall(r'\b\w+\b', cleaned.lower())
        
        # Filter out stop words and short words
        filtered_tokens = [
            token for token in tokens 
            if token not in self.stop_words and len(token) > 2 and token.isalpha()
        ]
        
        # Stem tokens
        stemmed_tokens = [self.stemmer.stem(token) for token in filtered_tokens]
        
        return {
            'original': text,
            'cleaned': cleaned,
            'sentences': sentences,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'stemmed_tokens': stemmed_tokens
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\-.,;:!?()[\]{}"\']', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'\b(\w)\1{3,}\b', r'\1\1', text)  # Remove repeated characters
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text using simple n-gram analysis."""
        processed = self.preprocess_text(text)
        tokens = processed['filtered_tokens']
        
        if len(tokens) < 2:
            return tokens
        
        # Generate bigrams and trigrams
        phrases = []
        
        # Bigrams
        for i in range(len(tokens) - 1):
            bigram = ' '.join(tokens[i:i+2])
            phrases.append(bigram)
        
        # Trigrams
        for i in range(len(tokens) - 2):
            trigram = ' '.join(tokens[i:i+3])
            phrases.append(trigram)
        
        # Count frequency and return top phrases
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Sort by frequency and return top phrases
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, count in sorted_phrases[:max_phrases]]
    
    def segment_text(self, text: str, segment_size: int = 200) -> List[Dict[str, Any]]:
        """
        Segment text into smaller chunks for analysis.
        
        Args:
            text: Text to segment
            segment_size: Target word count per segment
            
        Returns:
            List of text segments with metadata
        """
        processed = self.preprocess_text(text)
        sentences = processed['sentences']
        
        if not sentences:
            return []
        
        segments = []
        current_segment = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed segment size, save current segment
            if current_word_count + sentence_words > segment_size and current_segment:
                segment_text = ' '.join(current_segment)
                segments.append({
                    'text': segment_text,
                    'word_count': current_word_count,
                    'sentence_count': len(current_segment),
                    'processed': self.preprocess_text(segment_text)
                })
                current_segment = []
                current_word_count = 0
            
            current_segment.append(sentence)
            current_word_count += sentence_words
        
        # Add final segment
        if current_segment:
            segment_text = ' '.join(current_segment)
            segments.append({
                'text': segment_text,
                'word_count': current_word_count,
                'sentence_count': len(current_segment),
                'processed': self.preprocess_text(segment_text)
            })
        
        return segments
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using simple token overlap.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        processed1 = self.preprocess_text(text1)
        processed2 = self.preprocess_text(text2)
        
        tokens1 = set(processed1['stemmed_tokens'])
        tokens2 = set(processed2['stemmed_tokens'])
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def extract_named_entities(self, text: str) -> List[str]:
        """Extract potential named entities using simple patterns."""
        entities = []
        
        # Capitalized words (potential proper nouns)
        cap_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(cap_words)
        
        # Acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        entities.extend(acronyms)
        
        # Remove duplicates and common words
        entities = list(set(entities))
        entities = [e for e in entities if e.lower() not in self.stop_words]
        
        return entities[:20]  # Return top 20 entities
