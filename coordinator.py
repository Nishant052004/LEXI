import time
from database.connection import SessionLocal, engine, Base
from memory.memory_manager import memory_manager
from models.db_models import Conversation
from agents.registry import agent_registry
from agents.router import agent_router
from utils.logger import setup_logger
from utils.metrics import track_execution_time

logger = setup_logger("coordinator")

# Ensure all database tables exist on import/startup
Base.metadata.create_all(bind=engine)

@track_execution_time("Coordinator")
def decide_agent(messages: list, prompt: str) -> str:
    """
    Orchestrates the entire Multi-Agent pipeline, keeping compatibility with the existing
    Streamlit app while leveraging NLP, NER, database memory, routing, and Groq LLM.
    """
    logger.info(f"Coordinator received prompt: {prompt}")
    
    # 1. Open Database Session
    db = SessionLocal()
    try:
        # 2. Setup Default User & Conversation (Personalized for Nishant)
        # In a multi-user version, these would come from authentication contexts.
        username = "Nishant"
        default_user = memory_manager.get_or_create_user(db, username=username)
        
        # Reuse the latest conversation if we have message history, otherwise create a new one
        from sqlalchemy import desc
        default_convo = None
        if len(messages) > 1:
            default_convo = db.query(Conversation).filter(
                Conversation.user_id == default_user.id
            ).order_by(desc(Conversation.created_at)).first()
            
        if not default_convo:
            default_convo = memory_manager.get_or_create_conversation(db, user_id=default_user.id)
        
        # 3. Create Shared Multi-Agent Context
        context = {
            "db": db,
            "user_id": default_user.id,
            "username": default_user.username,
            "conversation_id": default_convo.id,
            "messages": messages
        }
        
        # Start timer for metrics
        start_time = time.perf_counter()
        
        # 4. Trigger NLP Agent to analyze intent, sentiment, keywords
        nlp_agent = agent_registry.get_agent("nlpagent")
        if nlp_agent:
            nlp_agent.execute(prompt, context)
            
        nlp_data = context.get("nlp_analysis", {})
        intent = nlp_data.get("intent", "general")
        sentiment = nlp_data.get("sentiment", "neutral")
        
        # 5. Trigger NER Agent to extract entities and save them in the DB
        ner_agent = agent_registry.get_agent("neragent")
        if ner_agent:
            ner_agent.execute(prompt, context)
            
        # 6. Route to specialized Agent based on intent
        selected_agent = agent_router.route(intent, prompt)
        if selected_agent:
            # Execute the selected specialist agent (e.g. ResearchAgent, CodingAgent)
            logger.info(f"Executing specialist: {selected_agent.name}")
            selected_agent.execute(prompt, context)
        
        # 7. Generate final response using the ResponseGenerationAgent
        response_agent = agent_registry.get_agent("responsegenerationagent")
        if response_agent:
            response_agent.execute(prompt, context)
            response = context.get("final_response", "Sorry, I could not generate a response.")
        else:
            response = "Error: Response Generation Agent is unregistered."
            
        execution_time = time.perf_counter() - start_time
        
        # 8. Log the complete interaction in the database
        memory_manager.log_interaction(
            db=db,
            conversation_id=default_convo.id,
            agent_name=selected_agent.name if selected_agent else "ResponseGenerationAgent",
            prompt=prompt,
            response=response,
            sentiment=sentiment,
            intent=intent,
            execution_time=execution_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Coordinator error: {str(e)}")
        # Fallback to direct Ask LLM or basic response if coordinator fails
        try:
            from llm import ask_llm
            messages.append({"role": "user", "content": prompt})
            return ask_llm(messages)
        except Exception:
            return f"Hi Nishant 👋, welcome back. I encountered an issue processing your request: {str(e)}"
    finally:
        db.close()