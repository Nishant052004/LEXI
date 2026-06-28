import re
import spacy
import spacy.cli
from spacy.pipeline import EntityRuler
from typing import Dict, Any, List, Tuple
from utils.logger import setup_logger

logger = setup_logger("ner_module")

class NERExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to loading it after downloading, or None
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None
                logger.error("spaCy not available for NERExtractor. Running regex fallback.")

        # Setup standard Regex patterns for emails and phone numbers
        self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')

        # Dynamic Custom Patterns list that the user can append to
        # Format: {"pattern": "Google DeepMind", "label": "ORG"} or regex rules
        self.custom_literal_patterns: List[Dict[str, str]] = []
        
        # Load custom patterns from DB
        self.load_custom_patterns_from_db()
        
        # Configure EntityRuler for custom patterns if spaCy is loaded
        if self.nlp:
            self._init_entity_ruler()

    def load_custom_patterns_from_db(self):
        """Loads custom entity mappings from the database dynamically."""
        try:
            from database.connection import SessionLocal
            from models.db_models import CustomEntityMapping
            db = SessionLocal()
            mappings = db.query(CustomEntityMapping).all()
            self.custom_literal_patterns = []
            for m in mappings:
                self.custom_literal_patterns.append({"label": m.label.upper(), "pattern": m.literal_text})
            db.close()
            logger.info(f"Loaded {len(self.custom_literal_patterns)} custom entity patterns from database.")
        except Exception as e:
            logger.warning(f"Could not load custom patterns from database (table may not exist yet): {str(e)}")

    def _init_entity_ruler(self):
        """Initializes or updates the spacy EntityRuler with custom rules."""
        # Check if ruler already exists in pipeline
        if "entity_ruler" in self.nlp.pipe_names:
            self.nlp.remove_pipe("entity_ruler")
        
        # Create EntityRuler and place it before standard 'ner' so custom matches override or combine
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        # Add basic pattern templates for emails and phones if we want spaCy to handle them as well
        patterns = [
            {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"}}]},
            # Add some custom user patterns loaded dynamically
            # Example: {"label": "PRODUCT", "pattern": "Antigravity"}
        ]
        
        # Load literal patterns from custom registry
        for lp in self.custom_literal_patterns:
            patterns.append({"label": lp["label"].upper(), "pattern": lp["pattern"]})
            
        ruler.add_patterns(patterns)

    def add_custom_entity_label(self, label: str, literal_text: str, save_to_db: bool = True):
        """Registers a new custom entity label dynamically at runtime and persists it."""
        label_upper = label.upper()
        # Avoid duplicate patterns in-memory
        if not any(lp["pattern"].lower() == literal_text.lower() for lp in self.custom_literal_patterns):
            self.custom_literal_patterns.append({"label": label_upper, "pattern": literal_text})
        
        if save_to_db:
            try:
                from database.connection import SessionLocal
                from models.db_models import CustomEntityMapping
                db = SessionLocal()
                # Check if already exists in DB
                existing = db.query(CustomEntityMapping).filter(
                    CustomEntityMapping.literal_text == literal_text
                ).first()
                if not existing:
                    new_mapping = CustomEntityMapping(label=label_upper, literal_text=literal_text)
                    db.add(new_mapping)
                    db.commit()
                db.close()
            except Exception as e:
                logger.error(f"Error saving custom entity pattern to DB: {str(e)}")

        logger.info(f"Added custom entity pattern: '{literal_text}' mapped to label '{label_upper}'")
        if self.nlp:
            self._init_entity_ruler()

    def remove_custom_entity_label(self, literal_text: str):
        """Removes a custom entity pattern dynamically at runtime from memory and database."""
        self.custom_literal_patterns = [
            lp for lp in self.custom_literal_patterns if lp["pattern"].lower() != literal_text.lower()
        ]
        
        try:
            from database.connection import SessionLocal
            from models.db_models import CustomEntityMapping
            db = SessionLocal()
            existing = db.query(CustomEntityMapping).filter(
                CustomEntityMapping.literal_text == literal_text
            ).first()
            if existing:
                db.delete(existing)
                db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error removing custom entity pattern from DB: {str(e)}")

        logger.info(f"Removed custom entity pattern for literal text: '{literal_text}'")
        if self.nlp:
            self._init_entity_ruler()


    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extracts Person, Organization, Location, Date, Email, Phone, and Custom Entities from text."""
        entities = []
        
        # 1. Extract Emails using Regex
        for match in self.email_pattern.finditer(text):
            entities.append({
                "text": match.group(),
                "label": "EMAIL",
                "start": match.start(),
                "end": match.end()
            })
            
        # 2. Extract Phone Numbers using Regex
        for match in self.phone_pattern.finditer(text):
            val = match.group().strip()
            # Basic validation: length must be reasonable (e.g. 7 to 15 digits or characters)
            digit_count = sum(1 for c in val if c.isdigit())
            if 7 <= digit_count <= 15:
                entities.append({
                    "text": val,
                    "label": "PHONE_NUMBER",
                    "start": match.start(),
                    "end": match.end()
                })

        # 3. Extract entities using spaCy
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # Map spaCy labels to requested format
                label_map = {
                    "PERSON": "PERSON",
                    "ORG": "ORGANIZATION",
                    "GPE": "LOCATION",
                    "LOC": "LOCATION",
                    "DATE": "DATE",
                    "EMAIL": "EMAIL"
                }
                label = label_map.get(ent.label_, ent.label_)
                
                # Check for duplicates from regex rules
                is_dup = any(
                    e["start"] == ent.start_char and e["end"] == ent.end_char 
                    for e in entities
                )
                if not is_dup:
                    entities.append({
                        "text": ent.text,
                        "label": label,
                        "start": ent.start_char,
                        "end": ent.end_char
                    })
        else:
            # Simple fallback entity extraction for when spaCy is unavailable
            # Mock PERSON, ORG, LOC extraction based on Capitalization if spaCy fails
            words = text.split()
            for idx, word in enumerate(words):
                clean_word = word.strip(".,!?;:()\"'")
                if clean_word.istitle() and clean_word.lower() not in ["the", "this", "that", "there", "their"]:
                    # Basic classification heuristic
                    label = "ORGANIZATION" if "inc" in clean_word.lower() or "corp" in clean_word.lower() else "PERSON"
                    start_idx = text.find(clean_word)
                    entities.append({
                        "text": clean_word,
                        "label": label,
                        "start": start_idx,
                        "end": start_idx + len(clean_word)
                    })

        # Sort entities by start index
        entities.sort(key=lambda x: x["start"])
        return entities

ner_extractor = NERExtractor()
