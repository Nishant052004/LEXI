import os
import sys
from pathlib import Path

# Add root folder to python path so we can run test from root directory
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from database.connection import SessionLocal, Base, engine
from memory.memory_manager import memory_manager
from nlp.nlp_module import nlp_processor
from ner.ner_module import ner_extractor
from services.auth_service import get_password_hash, verify_password, create_access_token, verify_token
from agents.registry import agent_registry
from agents.router import agent_router
from coordinator import decide_agent

def run_integration_tests():
    print("==================================================")
    print("       STARTING INTEGRATION TEST RUN             ")
    print("==================================================")
    
    # 1. Setup DB
    print("\n[1/6] Database Verification...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("Database tables initialized successfully.")

    # 2. Test Security & Auth Module
    print("\n[2/6] Security & Authentication Verification...")
    pwd = "secretpassword123"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    print("Password hashing and verification: PASS")
    
    token = create_access_token(subject="Nishant")
    username_from_token = verify_token(token)
    assert username_from_token == "Nishant"
    print("JWT Token creation and verification: PASS")

    # 3. Test User & Preference Memory
    print("\n[3/6] User Preference & Conversation Memory Verification...")
    user = memory_manager.get_or_create_user(db, username="Nishant", hashed_password=hashed, role="admin")
    assert user.username == "Nishant"
    print(f"Loaded user '{user.username}' with role '{user.role}'")
    
    prefs = {"theme": "dark", "temperature": 0.5}
    memory_manager.update_user_preferences(db, user.id, prefs)
    retrieved_prefs = memory_manager.get_user_preferences(db, user.id)
    assert retrieved_prefs["temperature"] == 0.5
    print("User preference write and retrieve: PASS")

    # 4. Test NLP & NER pipelines
    print("\n[4/6] NLP & NER Processing Verification...")
    prompt = "Hi Nishant, can you search for Google DeepMind's latest projects in London today? Contact them at contact@deepmind.com or call +44-20-1234-5678."
    
    nlp_results = nlp_processor.process_all(prompt)
    print(f"Prompt classified intent: {nlp_results['intent'].upper()}")
    print(f"Prompt sentiment: {nlp_results['sentiment'].upper()}")
    print(f"Keywords extracted: {nlp_results['keywords']}")
    assert nlp_results['intent'] == "research" # contains 'search' and 'today'

    # Register a custom entity first
    ner_extractor.add_custom_entity_label("COMPANY_BRAND", "Google DeepMind")
    entities = ner_extractor.extract_entities(prompt)
    
    print(f"Extracted {len(entities)} named entities:")
    email_found = False
    phone_found = False
    custom_found = False
    
    for ent in entities:
        print(f" - {ent['text']} ➔ [{ent['label']}]")
        if ent['label'] == "EMAIL":
            email_found = True
        if ent['label'] == "PHONE_NUMBER":
            phone_found = True
        if ent['label'] == "COMPANY_BRAND":
            custom_found = True
            
    assert email_found is True, "Should extract emails"
    assert phone_found is True, "Should extract phone numbers"
    assert custom_found is True, "Should extract custom literal COMPANY_BRAND"
    print("Named entity extraction metrics: PASS")

    # 5. Agent Router
    print("\n[5/6] Multi-Agent Routing Verification...")
    agent = agent_router.route("research", prompt)
    assert agent is not None
    assert agent.name == "ResearchAgent"
    print(f"Router properly resolved research intent to agent: {agent.name} (PASS)")

    # 6. Coordinator Orchestration Run
    print("\n[6/6] Orchestrator Loop Verification...")
    # Seed messages
    messages = []
    response = decide_agent(messages, "What are the latest news about AI today?")
    print("Assistant response generated successfully:")
    print("--------------------------------------------------")
    print(response)
    print("--------------------------------------------------")
    
    # Check that database logged the transaction
    from models.db_models import Conversation as DBConversation
    convo = db.query(DBConversation).filter(DBConversation.user_id == user.id).order_by(DBConversation.created_at.desc()).first()
    history = memory_manager.get_conversation_history(db, convo.id)
    assert len(history) >= 2
    print("Orchestrator DB transaction log: PASS")

    db.close()
    print("\n==================================================")
    print("       ALL SYSTEM COMPONENT TESTS PASSED!       ")
    print("==================================================")

if __name__ == "__main__":
    run_integration_tests()
