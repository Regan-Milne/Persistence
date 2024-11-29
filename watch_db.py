"""Script to watch the vector database in real-time"""

from vector_store import VectorStore
import time
from datetime import datetime
import os
from config import DEBUG_PRINTS

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def watch_database(refresh_rate=2):
    """Watch the database for changes with a specified refresh rate in seconds"""
    store = VectorStore()
    last_count = 0
    
    try:
        while True:
            clear_screen()
            
            # Get all documents
            result = store.collection.get()
            current_count = len(result['documents'])
            
            # Print header
            print(f"\n=== ChromaDB Watch ({datetime.now().strftime('%H:%M:%S')}) ===")
            print(f"Documents in database: {current_count}")
            
            # Show if there are new entries
            if current_count > last_count:
                print(f"\n[+] {current_count - last_count} new entries added!")
            
            if current_count > 0:
                print("\nLatest conversations:")
                print("-" * 50)
                
                # Sort by timestamp
                sorted_items = list(zip(result['documents'], result['metadatas']))
                sorted_items.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                
                # Show the 5 most recent entries
                for doc, meta in sorted_items[:5]:
                    print(f"\nTimestamp: {meta.get('timestamp', 'N/A')}")
                    print(f"Session: {meta.get('session', 'N/A')}")
                    try:
                        # Truncate long messages
                        content = doc if len(doc) < 100 else doc[:97] + "..."
                        print(f"Content: {content}")
                    except UnicodeEncodeError:
                        print("Content: [Unicode encoding error]")
                    print("-" * 50)
            
            last_count = current_count
            time.sleep(refresh_rate)
            
    except KeyboardInterrupt:
        print("\nStopping database watch...")

if __name__ == "__main__":
    print("Starting database watch (Press Ctrl+C to stop)...")
    watch_database()
