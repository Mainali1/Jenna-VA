"""Text Summarization Feature Implementation"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.cluster.util import cosine_distance
import numpy as np

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class TextSummarizer:
    """Implements text summarization using NLTK and extractive summarization techniques."""
    
    def __init__(self):
        self.logger = get_logger("text_summarizer")
        self.ensure_nltk_resources()
        self.stop_words = set(stopwords.words('english'))
    
    def ensure_nltk_resources(self) -> None:
        """Ensure that required NLTK resources are downloaded."""
        try:
            resources = [
                'punkt',
                'stopwords',
                'averaged_perceptron_tagger'
            ]
            
            for resource in resources:
                try:
                    nltk.data.find(f'tokenizers/{resource}')
                except LookupError:
                    self.logger.info(f"Downloading NLTK resource: {resource}")
                    nltk.download(resource, quiet=True)
        except Exception as e:
            self.logger.error(f"Error ensuring NLTK resources: {e}")
            raise FeatureManagerException(f"Failed to initialize NLTK resources: {e}")
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text by tokenizing into sentences and removing special characters."""
        # Tokenize text into sentences
        sentences = sent_tokenize(text)
        
        # Clean sentences
        clean_sentences = []
        for sentence in sentences:
            # Remove special characters and convert to lowercase
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word.isalnum()]
            clean_sentence = ' '.join(words)
            clean_sentences.append(clean_sentence)
        
        return clean_sentences
    
    def sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate the cosine similarity between two sentences."""
        # Tokenize sentences
        words1 = word_tokenize(sent1.lower())
        words2 = word_tokenize(sent2.lower())
        
        # Remove stop words
        words1 = [word for word in words1 if word not in self.stop_words]
        words2 = [word for word in words2 if word not in self.stop_words]
        
        # Create a set of all unique words
        all_words = list(set(words1 + words2))
        
        # Create word vectors
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)
        
        # Fill vectors
        for word in words1:
            if word in all_words:
                vector1[all_words.index(word)] += 1
        
        for word in words2:
            if word in all_words:
                vector2[all_words.index(word)] += 1
        
        # Calculate cosine similarity
        if sum(vector1) == 0 or sum(vector2) == 0:
            return 0.0
        
        return 1 - cosine_distance(vector1, vector2)
    
    def build_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """Build a similarity matrix for all sentences."""
        # Create an empty similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        
        # Fill the similarity matrix
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    similarity_matrix[i][j] = self.sentence_similarity(sentences[i], sentences[j])
        
        return similarity_matrix
    
    def pagerank(self, similarity_matrix: np.ndarray, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
        """Implement PageRank algorithm to rank sentences."""
        n = similarity_matrix.shape[0]
        
        # Initialize PageRank scores
        scores = np.ones(n) / n
        
        # Normalize the similarity matrix
        row_sums = similarity_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        transition_matrix = similarity_matrix / row_sums
        
        # PageRank iteration
        for _ in range(max_iter):
            prev_scores = scores.copy()
            scores = (1 - damping) / n + damping * (transition_matrix.T @ scores)
            
            # Check convergence
            if np.abs(scores - prev_scores).sum() < tol:
                break
        
        return scores
    
    def textrank_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Generate a summary using the TextRank algorithm."""
        # Preprocess text
        sentences = sent_tokenize(text)
        clean_sentences = self.preprocess_text(text)
        
        # If there are fewer sentences than requested, return the original text
        if len(sentences) <= num_sentences:
            return text
        
        # Build similarity matrix
        similarity_matrix = self.build_similarity_matrix(clean_sentences)
        
        # Apply PageRank algorithm
        scores = self.pagerank(similarity_matrix)
        
        # Rank sentences by score
        ranked_sentences = [(score, i, sentence) for i, (score, sentence) in enumerate(zip(scores, sentences))]
        ranked_sentences.sort(reverse=True)
        
        # Select top sentences and sort by original order
        top_sentences = ranked_sentences[:num_sentences]
        top_sentences.sort(key=lambda x: x[1])
        
        # Combine sentences into summary
        summary = ' '.join([sentence for _, _, sentence in top_sentences])
        
        return summary
    
    def frequency_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Generate a summary using word frequency analysis."""
        # Tokenize text
        sentences = sent_tokenize(text)
        
        # If there are fewer sentences than requested, return the original text
        if len(sentences) <= num_sentences:
            return text
        
        # Tokenize words and remove stop words
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Calculate word frequencies
        freq_dist = FreqDist(words)
        
        # Score sentences based on word frequencies
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word.isalnum() and word not in self.stop_words]
            
            for word in words:
                score += freq_dist[word]
            
            # Normalize by sentence length to avoid bias towards longer sentences
            if len(words) > 0:
                score /= len(words)
            
            sentence_scores.append((score, i, sentence))
        
        # Rank sentences by score
        sentence_scores.sort(reverse=True)
        
        # Select top sentences and sort by original order
        top_sentences = sentence_scores[:num_sentences]
        top_sentences.sort(key=lambda x: x[1])
        
        # Combine sentences into summary
        summary = ' '.join([sentence for _, _, sentence in top_sentences])
        
        return summary
    
    def hybrid_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Generate a summary using a hybrid of TextRank and frequency-based approaches."""
        # Get summaries from both methods
        textrank_summary = self.textrank_summarize(text, num_sentences)
        freq_summary = self.frequency_summarize(text, num_sentences)
        
        # Combine unique sentences from both summaries
        textrank_sentences = set(sent_tokenize(textrank_summary))
        freq_sentences = set(sent_tokenize(freq_summary))
        
        # Get unique sentences from each method
        unique_textrank = textrank_sentences - freq_sentences
        unique_freq = freq_sentences - textrank_sentences
        common = textrank_sentences.intersection(freq_sentences)
        
        # Prioritize common sentences, then add unique ones up to the limit
        final_sentences = list(common)
        
        # Add unique sentences from TextRank and frequency methods alternately
        unique_textrank = list(unique_textrank)
        unique_freq = list(unique_freq)
        
        i = 0
        while len(final_sentences) < num_sentences and (unique_textrank or unique_freq):
            if i % 2 == 0 and unique_textrank:
                final_sentences.append(unique_textrank.pop(0))
            elif unique_freq:
                final_sentences.append(unique_freq.pop(0))
            elif unique_textrank:  # If one list is empty but the other isn't
                final_sentences.append(unique_textrank.pop(0))
            i += 1
        
        # Find the original indices of these sentences in the text
        original_sentences = sent_tokenize(text)
        indices = []
        
        for summary_sentence in final_sentences:
            for i, original_sentence in enumerate(original_sentences):
                if summary_sentence == original_sentence:
                    indices.append(i)
                    break
        
        # Sort by original order
        indices.sort()
        
        # Get the sentences in the original order
        ordered_sentences = [original_sentences[i] for i in indices]
        
        # Combine sentences into summary
        summary = ' '.join(ordered_sentences)
        
        return summary
    
    def summarize(self, text: str, method: str = "hybrid", ratio: float = 0.3, max_sentences: int = 5) -> str:
        """Generate a summary of the given text.
        
        Args:
            text: The text to summarize
            method: The summarization method to use ("textrank", "frequency", or "hybrid")
            ratio: The ratio of sentences to include in the summary (0.0 to 1.0)
            max_sentences: The maximum number of sentences to include
        
        Returns:
            A string containing the summarized text
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        # Count the number of sentences in the original text
        sentences = sent_tokenize(text)
        num_sentences = max(1, min(int(len(sentences) * ratio), max_sentences))
        
        # Generate summary based on the selected method
        if method == "textrank":
            return self.textrank_summarize(text, num_sentences)
        elif method == "frequency":
            return self.frequency_summarize(text, num_sentences)
        else:  # hybrid or any other value
            return self.hybrid_summarize(text, num_sentences)


class SummarizationHistory:
    """Manages the history of text summarization requests."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "summarization"
        self.history: List[Dict[str, Any]] = []
        self.logger = get_logger("summarization_history")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_history(self) -> None:
        """Load summarization history from disk."""
        history_file = self.data_dir / "history.json"
        
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.logger.info(f"Loaded {len(self.history)} summarization entries from history")
            except Exception as e:
                self.logger.error(f"Error loading summarization history: {e}")
    
    async def save_history(self) -> None:
        """Save summarization history to disk."""
        history_file = self.data_dir / "history.json"
        
        try:
            # Keep only the most recent 100 entries to prevent the file from growing too large
            recent_history = self.history[-100:] if len(self.history) > 100 else self.history
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(recent_history, f, indent=2)
            self.logger.info(f"Saved {len(recent_history)} summarization entries to history")
        except Exception as e:
            self.logger.error(f"Error saving summarization history: {e}")
    
    def add_entry(self, original_text: str, summary: str, method: str) -> None:
        """Add a new entry to the summarization history."""
        from datetime import datetime
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "original_length": len(original_text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(original_text) if len(original_text) > 0 else 0,
            "original_text": original_text[:500] + "..." if len(original_text) > 500 else original_text,
            "summary": summary
        }
        
        self.history.append(entry)
        asyncio.create_task(self.save_history())
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent entries from the summarization history."""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def clear_history(self) -> None:
        """Clear the summarization history."""
        self.history = []
        asyncio.create_task(self.save_history())


class TextSummarizationManager:
    """Manages text summarization operations and history."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.summarizer = TextSummarizer()
        self.history = SummarizationHistory(data_dir)
        self.logger = get_logger("text_summarization")
    
    async def initialize(self) -> None:
        """Initialize the text summarization manager."""
        try:
            # Load summarization history
            await self.history.load_history()
            self.logger.info("Initialized TextSummarizationManager")
        except Exception as e:
            self.logger.error(f"Error initializing TextSummarizationManager: {e}")
            raise FeatureManagerException(f"Failed to initialize TextSummarizationManager: {e}")
    
    async def summarize_text(self, text: str, method: str = "hybrid", ratio: float = 0.3, max_sentences: int = 5) -> str:
        """Summarize the given text and add to history."""
        try:
            summary = self.summarizer.summarize(text, method, ratio, max_sentences)
            self.history.add_entry(text, summary, method)
            return summary
        except Exception as e:
            self.logger.error(f"Error summarizing text: {e}")
            raise FeatureManagerException(f"Failed to summarize text: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the summarization history."""
        return self.history.get_history(limit)
    
    def clear_history(self) -> None:
        """Clear the summarization history."""
        self.history.clear_history()
        self.logger.info("Cleared summarization history")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.history.save_history()
        self.logger.info("Cleaned up TextSummarizationManager")