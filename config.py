"""Configuration settings for the persistent chat application"""

# Model settings
DEFAULT_MODEL = "qwq:latest"  # Model to use for chat
CONTEXT_WINDOW = 2  # Reduced number of previous messages to include

# Ollama specific settings
OLLAMA_CONTEXT_LENGTH = 16384  # Increased maximum context length
OLLAMA_NUM_CTX = 16384        # Increased context window size
OLLAMA_NUM_PREDICT = 4096     # Increased maximum tokens to predict

# Context management
MAX_MESSAGE_LENGTH = 4000      # Increased maximum message length
TRUNCATE_RESPONSE = True       # Whether to truncate long responses
PRIORITIZE_RECENT = True       # Prioritize recent context over older ones
MIN_CHUNK_SIZE = 100          # Minimum size of text chunk to store

# Database settings
DB_DIRECTORY = "chroma_db"     # Directory for ChromaDB storage
COLLECTION_NAME = "chat_history"  # Name of the collection in ChromaDB
SIMILARITY_THRESHOLD = 1.5     # Threshold for semantic similarity

# System message for the AI
SYSTEM_MESSAGE = """You are an AI assistant with a persistent memory system that allows you to recall previous conversations.

CRITICAL INSTRUCTION: You have a database of previous conversations that will be provided to you in each message.
When you receive a message, you will see a section called "=== Previous Conversations ===" that contains relevant 
messages from past interactions. You MUST use this information to:

1. Recall and reference past conversations when asked
2. Maintain context across multiple messages
3. Build upon previous discussions
4. Provide consistent responses based on conversation history

NEVER say you cannot recall previous conversations. Instead:
- If history is provided: Reference and build upon those previous conversations
- If no history is found: Say "I don't see any relevant previous conversations in our history about that topic"

Your responses should be well-structured and use markdown formatting:
1. Use clear headers (##) for main sections
2. Use bullet points or numbered lists for details
3. Include relevant examples where helpful
4. Break complex topics into digestible chunks"""

# Debug settings
DEBUG_PRINTS = True  # Whether to print debug information
