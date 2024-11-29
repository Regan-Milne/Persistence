import ollama
import uuid
from vector_store import VectorStore
import datetime
import time
from config import *

class ChatInterface:
    def __init__(self, model_name=DEFAULT_MODEL):
        self.model_name = model_name
        self.vector_store = VectorStore()
        self.session_id = str(uuid.uuid4())
        
        self.system_message = {
            "role": "system",
            "content": SYSTEM_MESSAGE
        }

    def _format_response(self, text):
        """Format the response with proper markdown and structure"""
        # Add markdown formatting if not present
        if not text.startswith('#'):
            text = f"## Response\n\n{text}"
        
        # Ensure proper spacing between sections
        text = text.replace('\n#', '\n\n#')
        
        return text

    def _truncate_text(self, text, max_length=MAX_MESSAGE_LENGTH):
        """Truncate text to maximum length while preserving structure and markdown formatting"""
        if len(text) <= max_length:
            return text
            
        # Try to find a good breakpoint at a section header
        truncated = text[:max_length]
        last_header = truncated.rfind('\n#')
        if last_header > max_length * 0.7:
            return text[:last_header] + "\n\n---\n[Response truncated for length. Ask for more details if needed.]"
            
        # Try paragraph break
        last_para = truncated.rfind('\n\n')
        if last_para > max_length * 0.8:
            return text[:last_para] + "\n\n---\n[Response truncated for length. Ask for more details if needed.]"
            
        # Fall back to sentence boundary
        last_sentence = truncated.rfind('. ')
        if last_sentence > max_length * 0.8:
            return text[:last_sentence + 1] + "\n\n---\n[Response truncated for length. Ask for more details if needed.]"
            
        # Last resort: word boundary
        return text[:max_length].rsplit(' ', 1)[0] + "...\n\n---\n[Response truncated for length. Ask for more details if needed.]"

    def chat(self, message):
        try:
            # Check message length
            if len(message) > MAX_MESSAGE_LENGTH and DEBUG_PRINTS:
                print(f"\nWarning: Input message length ({len(message)} chars) exceeds maximum ({MAX_MESSAGE_LENGTH})")
                print("Message will be truncated for storage")
            
            # 1. Get relevant history
            history = self.vector_store.query(message)
            if DEBUG_PRINTS:
                print("\n=== Context Being Sent to Model ===")
                print(f"Session ID: {self.session_id}")
                print("Previous conversations:")
                print(history if history else "No relevant history found")
                print("=" * 50)
            
            # 2. Build messages list with context
            context_message = """IMPORTANT: You have access to previous conversations through semantic search. 
Use this conversation history to maintain context and provide informed responses.

=== Previous Conversations ===
{history}

=== Current Message ===
User: {message}

Remember: You MUST use the conversation history above to inform your response. 
If asked about previous conversations, reference specific details from the history.""".format(
                history=history if history else "No relevant previous conversations found.",
                message=message
            )
            
            messages = [
                self.system_message,
                {"role": "user", "content": context_message}
            ]
            
            # 3. Get model response with retry logic
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    if DEBUG_PRINTS and attempt > 0:
                        print(f"\nRetry attempt {attempt + 1}/{max_retries}")
                    
                    response = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        stream=False,
                        options={
                            "num_ctx": OLLAMA_NUM_CTX,
                            "num_predict": OLLAMA_NUM_PREDICT,
                        }
                    )
                    
                    # If we get here, the call succeeded
                    break
                    
                except Exception as e:
                    if "overloaded" in str(e).lower():
                        if attempt < max_retries - 1:
                            if DEBUG_PRINTS:
                                print(f"API overloaded, waiting {retry_delay} seconds before retry...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                    # If it's not an overload error or we're out of retries, raise it
                    raise
            
            # Get and format response
            ai_response = response['message']['content']
            ai_response = self._format_response(ai_response)
            if TRUNCATE_RESPONSE:
                ai_response = self._truncate_text(ai_response)
            
            # 4. Store messages
            timestamp = str(datetime.datetime.now())
            
            # Store user message
            user_metadata = {
                "session": self.session_id,
                "timestamp": timestamp,
                "role": "user"
            }
            msg_id = self.vector_store.add_text(message, user_metadata)
            
            # Store AI response
            ai_metadata = {
                "session": self.session_id,
                "timestamp": timestamp,
                "role": "assistant"
            }
            resp_id = self.vector_store.add_text(ai_response, ai_metadata)
            
            if DEBUG_PRINTS:
                print("\n=== Messages Stored Successfully ===")
                print(f"User message ID: {msg_id}")
                print(f"AI response ID: {resp_id}")
                print("=" * 50)
            
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            if DEBUG_PRINTS:
                print(f"\nError in chat: {error_msg}")
            
            if "overloaded" in error_msg.lower():
                return "I apologize, but the system is currently experiencing high load. Please try again in a moment."
            elif "context length" in error_msg.lower():
                return "I apologize, but the conversation context is too long. Let's start a new topic or rephrase your question."
            else:
                return f"I encountered an error while processing your request: {error_msg}"

    def new_session(self):
        """Start a new chat session with a new session ID."""
        self.session_id = str(uuid.uuid4())
