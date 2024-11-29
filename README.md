# Ollama Persistent Chat Interface

A chat interface for Ollama with persistent memory using ChromaDB vector database.

## Features

- Semantic search for conversation history
- Persistent memory across sessions
- Vector-based storage for better context retrieval
- Session management
- Error handling and graceful recovery

## Prerequisites

1. Ollama installed and running
2. Python 3.8+
3. The mistral-nemo:latest model pulled in Ollama

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Make sure Ollama is running and the model is installed:
```bash
ollama pull mistral-nemo:latest
```

## Usage

1. Run the chat interface:
```bash
python main.py
```

2. Available commands:
- Type 'quit' to exit
- Type 'new' to start a new session
- Any other input will be sent as a message to the chat

## How it Works

- Uses ChromaDB for vector-based storage of conversation history
- Semantically searches for relevant context from previous conversations
- Maintains persistent memory across different chat sessions
- Automatically manages conversation context window

## Directory Structure

- `main.py` - Entry point and CLI interface
- `chat_interface.py` - Main chat logic and Ollama integration
- `vector_store.py` - ChromaDB vector database operations
- `requirements.txt` - Python dependencies
- `chroma_db/` - Directory where ChromaDB stores its data (created automatically)
