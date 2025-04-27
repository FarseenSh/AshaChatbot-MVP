import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
import openrouter
from langchain_core.messages import HumanMessage, AIMessage
from job_listing_parser import JobListingProcessor
from bias_detection import BiasDetectionSystem
from session_processor import SessionProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("asha_ai.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AshaAI")

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

class AshaAI:
    """
    Main AshaAI class that integrates all components
    """
    
    def __init__(self):
        """
        Initialize the AshaAI system
        """
        logger.info("Initializing AshaAI...")
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Initialize components
        self._initialize_components()
        
        # Set up conversation memory
        self.memory = ConversationBufferMemory(return_messages=True)
        
        logger.info("AshaAI initialization complete")
    
    def _load_system_prompt(self) -> str:
        """
        Load the system prompt from file
        """
        try:
            with open("system_prompt.md", "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error loading system prompt: {str(e)}")
            # Use a default system prompt if file is not found
            return """
            You are Asha, an AI assistant for the JobsForHer Foundation. Your purpose is to help women advance 
            in their careers by providing information about job listings, community events, mentorship programs, 
            and addressing questions about women's career advancement. Focus on being supportive, empowering, 
            and helpful while avoiding gender bias.
            """
    
    def _initialize_components(self):
        """
        Initialize all components of the system
        """
        # Initialize job listing processor
        logger.info("Initializing job listing processor...")
        self.job_processor = JobListingProcessor()
        self.job_processor.load_data()
        self.job_processor.preprocess_data()
        self.job_processor.create_documents()
        self.job_processor.create_vector_store()
        
        # Initialize session processor
        logger.info("Initializing session processor...")
        self.session_processor = SessionProcessor()
        self.session_processor.load_data()
        self.session_processor.create_documents()
        self.session_processor.create_vector_store()
        
        # Initialize bias detection system
        logger.info("Initializing bias detection system...")
        self.bias_system = BiasDetectionSystem(api_key=OPENROUTER_API_KEY)
        
        # Initialize LLM with fixed OpenRouter configuration
        logger.info("Initializing LLM...")
        openrouter.api_key = OPENROUTER_API_KEY
    
    def generate_job_context(self, query: str) -> str:
        """
        Generate context based on job listings
        """
        # Search for relevant jobs
        relevant_jobs = self.job_processor.search_jobs(query, top_k=3)
        
        if not relevant_jobs:
            return "No relevant job information found."
        
        # Format job information
        job_context = "Here are some relevant job opportunities:\n\n"
        
        for i, job in enumerate(relevant_jobs):
            job_context += f"Job {i+1}: {job['job_title']} at {job['company_name']}\n"
            job_context += f"Location: {job['location']}\n"
            job_context += f"Job Type: {job['job_type']}\n"
            job_context += f"Remote Option: {job['remote_option']}\n"
            job_context += "\n"
        
        return job_context
    
    def generate_session_context(self, query: str) -> str:
        """
        Generate context based on session/event listings
        """
        # Search for relevant sessions
        relevant_sessions = self.session_processor.search_sessions(query, top_k=2)
        
        if not relevant_sessions:
            # If no relevant sessions found, return upcoming sessions
            upcoming_sessions = self.session_processor.get_upcoming_sessions(3)
            if not upcoming_sessions:
                return "No relevant event information found."
            
            session_context = "Here are some upcoming events that might interest you:\n\n"
            
            for i, session in enumerate(upcoming_sessions):
                session_context += f"Event {i+1}: {session['session_name']}\n"
                session_context += f"Date: {session['date']}\n"
                session_context += f"Type: {session['type']}\n"
                session_context += f"Location: {session['location']}\n"
                session_context += "\n"
            
            return session_context
        
        # Format session information
        session_context = "Here are some relevant events:\n\n"
        
        for i, session in enumerate(relevant_sessions):
            session_context += f"Event {i+1}: {session['session_name']}\n"
            session_context += f"Date: {session['session_date']}\n"
            session_context += f"Type: {session['session_type']}\n"
            session_context += f"Location: {session['location']}\n"
            session_context += f"Speaker: {session['speaker']}\n"
            session_context += "\n"
        
        return session_context
    
    def process_query(self, query: str, chat_history: List[List[str]]) -> Dict[str, Any]:
        """
        Process a user query and generate a response
        
        Args:
            query: User query
            chat_history: Gradio chat history
            
        Returns:
            Dictionary with response and additional information
        """
        logger.info(f"Processing query: {query}")
        start_time = time.time()
        
        try:
            # Check for bias
            empowerment_response, bias_info = self.bias_system.handle_biased_query(query)
            
            # If bias is detected, use the empowerment response
            if bias_info.get("has_bias", False):
                logger.info(f"Bias detected: {bias_info.get('bias_type')}")
                
                # Get the reframed query for context generation
                reframed_query = self.bias_system.get_reframed_query(bias_info)
                
                # Generate job context using the reframed query
                job_context = self.generate_job_context(reframed_query)
                
                # Generate session context using the reframed query
                session_context = self.generate_session_context(reframed_query)
                
                # Combine empowerment response with context
                response = f"{empowerment_response}\n\n{job_context}\n\n{session_context}"
                
                # Update memory with the original query and response
                self.memory.chat_memory.add_user_message(query)
                self.memory.chat_memory.add_ai_message(response)
                
                # Get job recommendations
                job_recommendations = self.job_processor.search_jobs(reframed_query)
                
                processing_time = time.time() - start_time
                logger.info(f"Response generated in {processing_time:.2f} seconds")
                
                return {
                    "response": response,
                    "has_bias": True,
                    "bias_info": bias_info,
                    "job_recommendations": job_recommendations,
                    "processing_time": processing_time
                }
            
            # For non-biased queries, generate context
            job_context = self.generate_job_context(query)
            session_context = self.generate_session_context(query)
            
            # Combine contexts
            combined_context = f"{job_context}\n\n{session_context}"
            
            # Convert chat history to messages
            messages = []
            for user_msg, bot_msg in chat_history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
            
            # Add system prompt and current query
            formatted_messages = [
                {"role": "system", "content": self.system_prompt},
                *messages,
                {"role": "user", "content": f"{query}\n\nContext from JobsForHer database:\n{combined_context}"}
            ]
            
            # Generate response using LLM with fixed OpenRouter API
            llm_response = openrouter.chat.completions.create(
                model="google/gemini-2.5-pro",
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            response = llm_response.choices[0].message.content
            
            # Update memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response)
            
            # Get job recommendations
            job_recommendations = self.job_processor.search_jobs(query)
            
            processing_time = time.time() - start_time
            logger.info(f"Response generated in {processing_time:.2f} seconds")
            
            return {
                "response": response,
                "has_bias": False,
                "bias_info": None,
                "job_recommendations": job_recommendations,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            processing_time = time.time() - start_time
            
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again.",
                "has_bias": False,
                "bias_info": None,
                "job_recommendations": [],
                "processing_time": processing_time,
                "error": str(e)
            }

    def get_upcoming_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get upcoming events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of upcoming events
        """
        return self.session_processor.get_upcoming_sessions(limit)


# Example standalone usage
if __name__ == "__main__":
    import gradio as gr
    
    # Initialize AshaAI
    asha_ai = AshaAI()
    
    # Define Gradio interface
    with gr.Blocks(css="footer {visibility: hidden}") as demo:
        gr.Markdown("# AshaAI - JobsForHer Foundation Chatbot")
        gr.Markdown("""
        Welcome to AshaAI, your career assistant from JobsForHer Foundation. 
        I can help you with:
        - Finding job opportunities
        - Information about community events and mentorship programs
        - Answering questions about women's career advancement
        - Providing insights on women's empowerment initiatives globally
        """)
        
        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            height=500
        )
        
        msg = gr.Textbox(
            show_label=False,
            placeholder="Ask me about jobs, events, or career advancement...",
            container=False
        )
        
        clear = gr.Button("Clear")
        
        def respond(message, chat_history):
            if not message.strip():
                return "", chat_history
                
            result = asha_ai.process_query(message, chat_history)
            bot_message = result["response"]
            
            # Add bias warning if needed
            if result.get("has_bias", False):
                bot_message += "\n\n(Note: I've provided factual information that promotes equality and empowerment.)"
                
            chat_history.append((message, bot_message))
            return "", chat_history
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
        
        gr.Markdown("""
        ## About AshaAI
        
        AshaAI is an initiative by JobsForHer Foundation to provide career guidance and support to women.
        The chatbot is designed to be inclusive, empowering, and helpful in your career journey.
        
        For more information, visit [JobsForHer](https://www.jobsforher.com/).
        """)
    
    # Launch the interface
    demo.launch(share=True)
