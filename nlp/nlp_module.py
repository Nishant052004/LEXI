import re
import spacy
import nltk
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("nlp_module")

# Pre-bootstrap check for NLTK and spaCy downloads
def bootstrap_nlp_resources():
    # NLTK resources
    resources = {
        'vader_lexicon': 'sentiment/vader_lexicon.zip',
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords'
    }
    for res_name, res_path in resources.items():
        try:
            nltk.data.find(res_path)
        except LookupError:
            logger.info(f"Downloading NLTK resource: {res_name}")
            nltk.download(res_name, quiet=True)

    # spaCy model
    global nlp, spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.info("Downloading spaCy model 'en_core_web_sm'...")
        import spacy.cli
        try:
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.error(f"Failed to download spaCy model automatically: {str(e)}")
            # Fallback to simple parser if spaCy fails to install
            nlp = None

bootstrap_nlp_resources()
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class NLPProcessor:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.intent_patterns = {
            "coding": [r"\bcode\b", r"\bfunction\b", r"\bpython\b", r"\bprogram\b", r"\bwrite a script\b", r"\bclass\b", r"\bcompile\b", r"\bbug\b", r"\bdevelop\b"],
            "research": [r"\bsearch\b", r"\bgoogle\b", r"\bfind out\b", r"\bwhat is\b", r"\bwho is\b", r"\bnews\b", r"\blatest\b", r"\btoday\b", r"\binternet\b"],
            "memory": [r"\bremember\b", r"\bmy preference\b", r"\bforget\b", r"\bhistory\b", r"\bwhat did we say\b", r"\bmy name\b"],
            "ner": [r"\bextract\b", r"\bentities\b", r"\bphone number\b", r"\bemail\b", r"\bdate\b", r"\bnames\b", r"\blocations\b"],
            "greeting": [r"\bhi\b", r"\bhello\b", r"\bgreet\b", r"\bhey\b", r"\bwelcome\b", r"\bgood morning\b", r"\bgood afternoon\b"]
        }

    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """Preprocesses text: tokenization, stopword removal, and lemmatization."""
        if not nlp:
            # Fallback preprocessing
            tokens = text.lower().split()
            return {"tokens": tokens, "lemmas": tokens, "cleaned_text": text.lower()}
            
        doc = nlp(text)
        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        cleaned_text = " ".join(lemmas)
        
        return {
            "tokens": tokens,
            "lemmas": lemmas,
            "cleaned_text": cleaned_text
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Performs sentiment analysis on text using NLTK VADER."""
        scores = self.sia.polarity_scores(text)
        compound = scores["compound"]
        
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "scores": scores
        }

    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extracts significant keywords (nouns, proper nouns, adjectives)."""
        if not nlp:
            # Fallback simple keyword extraction
            words = [w.lower() for w in text.split() if len(w) > 4]
            return list(set(words))[:max_keywords]
            
        doc = nlp(text)
        keywords = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop:
                keywords.append(token.lemma_.lower())
                
        # Deduplicate and limit
        seen = set()
        dedup_keywords = [k for k in keywords if not (k in seen or seen.add(k))]
        return dedup_keywords[:max_keywords]

    def classify_intent(self, text: str) -> str:
        """Classifies the primary intent of the user prompt using keyword patterns."""
        text_lower = text.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        return "general"  # Fallback intent for general response generation

    def categorize_query(self, text: str) -> str:
        """Categorizes the query type into transactional, informational, navigation, or conversational."""
        intent = self.classify_intent(text)
        if intent in ["greeting", "memory"]:
            return "conversational"
        elif intent in ["research", "ner"]:
            return "informational"
        elif intent in ["coding"]:
            return "transactional"
        return "informational"

    def process_all(self, text: str) -> Dict[str, Any]:
        """Runs the complete NLP pipeline on the input text."""
        preprocess = self.preprocess_text(text)
        sentiment = self.analyze_sentiment(text)
        keywords = self.extract_keywords(text)
        intent = self.classify_intent(text)
        category = self.categorize_query(text)
        
        return {
            "text": text,
            "preprocessed": preprocess,
            "sentiment": sentiment["sentiment"],
            "sentiment_scores": sentiment["scores"],
            "keywords": keywords,
            "intent": intent,
            "category": category
        }

nlp_processor = NLPProcessor()
