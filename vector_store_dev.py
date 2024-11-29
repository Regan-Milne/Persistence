import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import uuid
from datetime import datetime
import os
import logging
import sys

class VectorStore:
    def __init__(self, persist_directory=None):
        try:
            print("\nVectorStore: Starting initialization...")
            if persist_directory is None:
                # Use an absolute path in the project directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                persist_directory = os.path.join(current_dir, "chroma_db_dev")
                print(f"VectorStore: Using persist directory: {persist_directory}")
                
            # Ensure the directory exists
            os.makedirs(persist_directory, exist_ok=True)
            print("VectorStore: Directory created/verified")
            
            print("VectorStore: Initializing embedding function...")
            try:
                # Using a smaller, more stable model
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="paraphrase-MiniLM-L3-v2",
                    device="cpu"  # Explicitly use CPU
                )
                print("VectorStore: Embedding function initialized successfully")
            except Exception as e:
                print(f"VectorStore: Error initializing embedding function: {str(e)}")
                print("VectorStore: Full traceback:")
                import traceback
                traceback.print_exc(file=sys.stdout)
                raise
                
            print("VectorStore: Creating ChromaDB client...")
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            print("VectorStore: ChromaDB client created successfully")
            
            print("VectorStore: Setting up collection...")
            self.collection = self.client.get_or_create_collection(
                name="chat_history",
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.embedding_function
            )
            print("VectorStore: Collection setup complete")
            print("VectorStore: Initialization successful!")
            
        except Exception as e:
            print("\nVectorStore: Critical error during initialization:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Full traceback:")
            import traceback
            traceback.print_exc(file=sys.stdout)
            raise

    def add_message(self, role, content, session_id):
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        try:
            print(f"\nVectorStore: Adding message...")
            print(f"Role: {role}")
            print(f"Session: {session_id}")
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "role": role,
                    "session_id": session_id,
                    "timestamp": timestamp
                }],
                ids=[message_id]
            )
            print("VectorStore: Message added successfully")
        except Exception as e:
            print(f"Error adding message: {str(e)}")
            raise

    def get_relevant_history(self, query, n_results=5):
        try:
            print(f"\nVectorStore: Searching for relevant history...")
            print(f"Query: {query}")
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results or not results['documents']:
                print("VectorStore: No relevant history found")
                return ""
                
            # Format the results into a conversation history
            history = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                role = metadata['role'].capitalize()
                history.append(f"{role}: {doc}")
                
            print(f"VectorStore: Found {len(history)} relevant messages")
            return "\n".join(history)
            
        except Exception as e:
            print(f"Error retrieving history: {str(e)}")
            return ""  # Return empty string on error to allow conversation to continue
