from vector_store import VectorStore
import sys
from config import DEBUG_PRINTS

# Set console to UTF-8 mode
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

def check_database():
    try:
        # Get the VectorStore instance
        store = VectorStore()
        
        # Get all documents directly from the collection
        result = store.collection.get()
        
        print(f"\nFound {len(result['documents'])} documents in the database:")
        print("-" * 50)
        
        # Sort by timestamp if available
        sorted_items = list(zip(result['documents'], result['metadatas']))
        sorted_items.sort(key=lambda x: x[1].get('timestamp', ''))
        
        for doc, meta in sorted_items:
            print(f"\nSession: {meta.get('session', 'N/A')}")
            print(f"Timestamp: {meta.get('timestamp', 'N/A')}")
            try:
                print(f"Content: {doc}")
            except UnicodeEncodeError:
                print(f"Content: {doc.encode('utf-8', 'replace').decode()}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()
