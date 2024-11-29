# Ollama Persistent Memory Chat Interface

## Project Overview
A Python-based chat application that provides persistent memory capabilities for Ollama's Mistral-Nemo model using ChromaDB for semantic search and context retrieval.

## Features
- Cross-session memory persistence using vector database
- Dark mode GUI interface
- Semantic context retrieval
- Thread-safe message handling
- Session management

## Technical Stack
- **Python 3.8+**
- **Core Libraries:**
  - ollama (v0.1.6)
  - chromadb (v0.4.22)
  - sentence-transformers (v2.2.2)
  - tkinter (GUI)
  - python-dotenv (v1.0.0)
- **AI Model:** mistral-nemo:latest

## Components

### 1. Main GUI (main.py)
- Tkinter-based user interface
- Dark mode theme (#1a1a1a background, #4ae1dc text)
- Thread-safe message handling
- Session management controls

### 2. Chat Interface (chat_interface.py)
- Manages communication with Ollama
- Handles context retrieval and message processing
- Implements cross-session memory management
- Custom system prompt for consistent behavior

### 3. Vector Store (vector_store.py)
- ChromaDB integration for persistent storage
- Sentence transformer embeddings
- Semantic search capabilities
- Message metadata tracking

## Setup Instructions
1. Ensure Ollama is installed and running
2. Create a virtual environment (recommended)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Environment Requirements
- Windows/Linux/MacOS
- Python 3.8 or higher
- Ollama server running locally
- Sufficient disk space for ChromaDB storage

## Usage
1. Start the application
2. Type messages in the input field
3. Press Enter or click Send to chat
4. Use "New Session" to start a fresh conversation
5. Previous context is automatically retrieved when relevant

## Project Structure
```
Persistence/
├── main.py              # Main GUI and application entry
├── chat_interface.py    # Ollama communication layer
├── vector_store.py      # ChromaDB persistence layer
├── requirements.txt     # Project dependencies
└── chroma_db/          # Vector database storage
```

## Future Improvements
1. Conversation summarization
2. Advanced context management
3. Configuration options
4. Comprehensive logging
5. Unit tests
6. Encryption for stored conversations

## Known Issues
- Initialization can be slow due to model loading
- Memory usage grows with conversation history
- Requires manual Ollama server management

## Contributing
Feel free to submit issues and enhancement requests!
