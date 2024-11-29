import chromadb
import uuid
from datetime import datetime
import os
from config import *

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Use config settings for database setup
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.persist_directory = os.path.join(current_dir, DB_DIRECTORY)
            
        if DEBUG_PRINTS:
            print(f"\nUsing VectorStore directory: {self.persist_directory}")
            
        # Ensure the directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
            
        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )
        
        if DEBUG_PRINTS:
            print("ChromaDB client initialized")
        
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            if DEBUG_PRINTS:
                print(f"Found existing collection '{COLLECTION_NAME}'")
        except ValueError:
            # Create new collection if it doesn't exist
            if DEBUG_PRINTS:
                print(f"Creating new collection '{COLLECTION_NAME}'")
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        
        self._initialized = True

    def add_text(self, content, metadata):
        """Add a text entry to the vector store"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[{**metadata, "timestamp": timestamp}],
                ids=[message_id]
            )
            if DEBUG_PRINTS:
                print(f"Added text to vector store with ID: {message_id}")
            return message_id
        except Exception as e:
            if DEBUG_PRINTS:
                print(f"Error adding text to vector store: {e}")
            raise

    def query(self, query_text, n_results=CONTEXT_WINDOW):
        """Query the vector store for similar texts"""
        try:
            if DEBUG_PRINTS:
                print("\n=== Querying Vector Store ===")
                print(f"Query: {query_text}")
                print(f"Max results: {n_results}")
                print(f"Similarity threshold: {SIMILARITY_THRESHOLD}")
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                if DEBUG_PRINTS:
                    print("No results found")
                return None
                
            # Format messages with role and apply similarity threshold
            formatted_messages = []
            if DEBUG_PRINTS:
                print("\nMatched messages:")
            
            for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
                if DEBUG_PRINTS:
                    print(f"- Distance: {dist:.3f}, Role: {meta.get('role', 'unknown')}")
                
                # Only include if similarity is good enough
                if dist < SIMILARITY_THRESHOLD:
                    role = meta.get('role', 'unknown')
                    timestamp = meta.get('timestamp', '')[:19]  # Get just the date and time, not microseconds
                    formatted_messages.append(f"[{timestamp}] {role.capitalize()}: {doc}")
                elif DEBUG_PRINTS:
                    print("  (Excluded due to similarity threshold)")
            
            if DEBUG_PRINTS:
                print(f"\nReturning {len(formatted_messages)} relevant messages")
            
            if formatted_messages:
                history = "Here are the relevant messages from our conversation history:\n\n"
                history += "\n".join(formatted_messages)
                return history
            return None
            
        except Exception as e:
            if DEBUG_PRINTS:
                print(f"Error querying vector store: {e}")
            return None

    def reset_database(self):
        """Safely reset the database by deleting and recreating the collection"""
        try:
            # Delete the existing collection
            self.client.delete_collection(COLLECTION_NAME)
            if DEBUG_PRINTS:
                print(f"Deleted collection '{COLLECTION_NAME}'")
            
            # Create a new collection
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            if DEBUG_PRINTS:
                print(f"Created new collection '{COLLECTION_NAME}'")
            
            return True
        except Exception as e:
            if DEBUG_PRINTS:
                print(f"Error resetting database: {e}")
            return False
