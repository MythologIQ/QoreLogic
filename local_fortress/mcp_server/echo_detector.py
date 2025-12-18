"""
Q-DNA Echo/Paraphrase Detector

Phase 9: ML-Dependent Features
Spec Reference: §5.2 (Citation Policy), INFORMATION_THEORY.md

Detects when text is being echoed/paraphrased without proper attribution.
Uses N-gram overlap and Jaccard similarity for detection.

Research:
- 0.94 decay per citation hop (INFORMATION_THEORY.md)
- >60% overlap indicates substantial similarity
- N-grams (3-4 grams) capture phrase-level patterns
"""

import re
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class EchoResult:
    """Result of echo/paraphrase detection."""
    is_echo: bool
    similarity_score: float
    matching_ngrams: int
    total_ngrams: int
    detection_method: str
    rationale: str
    
    def to_dict(self) -> dict:
        return {
            "is_echo": self.is_echo,
            "similarity_score": round(self.similarity_score, 4),
            "matching_ngrams": self.matching_ngrams,
            "total_ngrams": self.total_ngrams,
            "detection_method": self.detection_method,
            "rationale": self.rationale
        }


class EchoDetector:
    """
    Detects echo/paraphrase content using N-gram similarity.
    
    Per INFORMATION_THEORY.md:
    - >60% overlap suggests substantial similarity (echo)
    - Uses 3-gram and 4-gram for phrase-level detection
    - Jaccard coefficient for set-based similarity
    """
    
    # Thresholds per INFORMATION_THEORY.md
    ECHO_THRESHOLD = 0.60  # >60% overlap = echo
    WARN_THRESHOLD = 0.40  # 40-60% = warning zone
    
    # N-gram sizes for phrase detection
    NGRAM_SIZES = [3, 4]  # Trigrams and 4-grams
    
    def __init__(self, echo_threshold: float = 0.60):
        """
        Initialize the echo detector.
        
        Args:
            echo_threshold: Similarity score above which content is flagged as echo
        """
        self.echo_threshold = echo_threshold
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into lowercase words.
        Removes punctuation and normalizes whitespace.
        """
        # Normalize: lowercase, remove punctuation, split on whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 1]  # Filter single chars
    
    def extract_ngrams(self, tokens: List[str], n: int) -> Set[Tuple[str, ...]]:
        """
        Extract n-grams from a list of tokens.
        
        Args:
            tokens: List of word tokens
            n: Size of n-grams
            
        Returns:
            Set of n-gram tuples
        """
        if len(tokens) < n:
            return set()
        
        ngrams = set()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            ngrams.add(ngram)
        
        return ngrams
    
    def jaccard_similarity(self, set_a: Set, set_b: Set) -> float:
        """
        Calculate Jaccard similarity coefficient.
        
        J(A,B) = |A ∩ B| / |A ∪ B|
        """
        if not set_a and not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def overlap_coefficient(self, set_a: Set, set_b: Set) -> float:
        """
        Calculate Overlap coefficient (Szymkiewicz-Simpson).
        
        O(A,B) = |A ∩ B| / min(|A|, |B|)
        
        More lenient than Jaccard - detects when smaller text is contained in larger.
        """
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        min_size = min(len(set_a), len(set_b))
        
        return intersection / min_size if min_size > 0 else 0.0
    
    def detect_echo(
        self,
        text_a: str,
        text_b: str,
        use_overlap: bool = True
    ) -> EchoResult:
        """
        Detect if text_b is an echo/paraphrase of text_a.
        
        Args:
            text_a: Original/source text
            text_b: Text to check for echo
            use_overlap: Use overlap coefficient (True) or Jaccard (False)
            
        Returns:
            EchoResult with detection details
        """
        # Tokenize both texts
        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)
        
        if len(tokens_a) < 5 or len(tokens_b) < 5:
            return EchoResult(
                is_echo=False,
                similarity_score=0.0,
                matching_ngrams=0,
                total_ngrams=0,
                detection_method="N/A",
                rationale="Text too short for meaningful comparison (<5 tokens)"
            )
        
        # Collect n-grams for all sizes
        all_ngrams_a: Set[Tuple[str, ...]] = set()
        all_ngrams_b: Set[Tuple[str, ...]] = set()
        
        for n in self.NGRAM_SIZES:
            all_ngrams_a.update(self.extract_ngrams(tokens_a, n))
            all_ngrams_b.update(self.extract_ngrams(tokens_b, n))
        
        # Calculate similarity
        if use_overlap:
            similarity = self.overlap_coefficient(all_ngrams_a, all_ngrams_b)
            method = "overlap_coefficient"
        else:
            similarity = self.jaccard_similarity(all_ngrams_a, all_ngrams_b)
            method = "jaccard"
        
        matching = len(all_ngrams_a & all_ngrams_b)
        total = len(all_ngrams_a | all_ngrams_b)
        
        # Determine result
        is_echo = similarity >= self.echo_threshold
        
        if is_echo:
            rationale = f"High similarity ({similarity:.1%}) exceeds echo threshold ({self.echo_threshold:.0%})"
        elif similarity >= self.WARN_THRESHOLD:
            rationale = f"Moderate similarity ({similarity:.1%}) in warning zone"
        else:
            rationale = f"Low similarity ({similarity:.1%}) below thresholds"
        
        return EchoResult(
            is_echo=is_echo,
            similarity_score=similarity,
            matching_ngrams=matching,
            total_ngrams=total,
            detection_method=method,
            rationale=rationale
        )
    
    def detect_self_echo(self, text: str, window_size: int = 200) -> List[EchoResult]:
        """
        Detect internal repetition/echoing within a single text.
        Useful for detecting copy-paste patterns.
        
        Args:
            text: Text to analyze
            window_size: Character window for comparison
            
        Returns:
            List of echo results for detected repetitions
        """
        results = []
        
        # Split into chunks
        chunks = []
        for i in range(0, len(text), window_size):
            chunk = text[i:i + window_size]
            if len(chunk) > 50:  # Minimum chunk size
                chunks.append((i, chunk))
        
        # Compare each chunk with subsequent chunks
        for i, (pos_a, chunk_a) in enumerate(chunks):
            for pos_b, chunk_b in chunks[i + 2:]:  # Skip adjacent
                result = self.detect_echo(chunk_a, chunk_b)
                if result.is_echo or result.similarity_score >= self.WARN_THRESHOLD:
                    result.rationale = f"Internal echo at positions {pos_a} and {pos_b}: {result.rationale}"
                    results.append(result)
        
        return results


# Convenience singleton
_detector: Optional[EchoDetector] = None


def get_echo_detector() -> EchoDetector:
    """Get or create the global echo detector instance."""
    global _detector
    if _detector is None:
        _detector = EchoDetector()
    return _detector


def check_echo(text_a: str, text_b: str) -> EchoResult:
    """
    Quick helper to check if text_b echoes text_a.
    
    Returns:
        EchoResult with is_echo flag and similarity score
    """
    return get_echo_detector().detect_echo(text_a, text_b)


# Unit test examples
if __name__ == "__main__":
    detector = EchoDetector()
    
    # Test 1: Clear echo (high similarity)
    original = "The quick brown fox jumps over the lazy dog near the river."
    echo = "The quick brown fox jumps over the lazy dog near the stream."
    result = detector.detect_echo(original, echo)
    print(f"Test 1 (Echo): {result.to_dict()}")
    
    # Test 2: Paraphrase (moderate similarity)
    paraphrase = "A fast brown fox leaps across a sleepy canine by the water."
    result = detector.detect_echo(original, paraphrase)
    print(f"Test 2 (Paraphrase): {result.to_dict()}")
    
    # Test 3: Different content (low similarity)
    different = "Machine learning models require large datasets for training."
    result = detector.detect_echo(original, different)
    print(f"Test 3 (Different): {result.to_dict()}")
    
    # Test 4: Self-echo detection
    repeated = original * 3
    results = detector.detect_self_echo(repeated)
    print(f"Test 4 (Self-echo): Found {len(results)} internal repetitions")
