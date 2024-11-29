from vector_store import VectorStore
import time
from config import DEBUG_PRINTS

def test_db():
    try:
        # Get VectorStore instance
        store = VectorStore.get_instance()
        
        # Test writing
        print("\nTesting write...")
        test_message = "This is a test message"
        metadata = {
            "test": "true",
            "timestamp": str(time.time()),
            "session": "test_session"
        }
        message_id = store.add_text(test_message, metadata)
        print(f"Added test message with ID: {message_id}")
        
        # Test reading
        print("\nTesting read...")
        results = store.query("test message")
        if results:
            print(f"Query results: {results}")
            return True
        else:
            print("No results found")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_db()
    print(f"\nTest {'passed' if success else 'failed'}")
