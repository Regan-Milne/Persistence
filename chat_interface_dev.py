import ollama
import uuid
from vector_store_dev import VectorStore
import sys
import traceback

class ChatInterface:
    def __init__(self, model_name="mistral-nemo:latest", context_window=5):
        try:
            print("ChatInterface: Starting initialization...")
            self.model_name = model_name
            print("ChatInterface: Creating VectorStore...")
            self.vector_store = VectorStore()
            print("ChatInterface: VectorStore created successfully")
            self.session_id = str(uuid.uuid4())
            self.context_window = context_window
            
            print("ChatInterface: Setting up system message...")
            # Updated system message to preserve model personality while maintaining memory rules
            self.system_message = {
                "role": "system",
                "content": """You are Mistral, a highly capable AI assistant known for being direct, knowledgeable, and occasionally playful. While you maintain your natural personality, you have access to a conversation history through a vector database.

Please follow these guidelines for memory management:
1. Only reference conversations that are explicitly provided in the context
2. If no previous context is given, engage naturally as you would in a fresh conversation
3. When mentioning past conversations, be specific about what was actually discussed
4. Don't reference dates or times unless they're explicitly provided
5. If unsure about previous discussions, continue the conversation naturally without making assumptions

Remember to be yourself while following these memory guidelines."""
            }
            print("ChatInterface: Initialization complete!")
            
        except Exception as e:
            print("ChatInterface: Error during initialization:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Traceback:")
            traceback.print_exc(file=sys.stdout)
            raise

    def chat(self, message):
        # Get semantically relevant conversation history across all sessions
        try:
            cross_session_history = self.vector_store.get_relevant_history(message)
            
            # Format messages for the conversation
            messages = [self.system_message]
            
            # Add context from previous conversations if available
            if cross_session_history:
                messages.append({
                    "role": "system",
                    "content": "Here are some relevant messages from previous conversations:\n" + cross_session_history
                })
            
            # Add the current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Get response from Ollama
            response = ollama.chat(model=self.model_name, messages=messages)
            assistant_message = response['message']['content']
            
            # Store both the user message and assistant's response
            self.vector_store.add_message("user", message, self.session_id)
            self.vector_store.add_message("assistant", assistant_message, self.session_id)
            
            return assistant_message
            
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            raise

    def new_session(self):
        """Start a new chat session with a new session ID."""
        self.session_id = str(uuid.uuid4())
