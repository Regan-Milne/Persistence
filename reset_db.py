"""Script to safely reset the vector database"""

from vector_store import VectorStore

def main():
    print("WARNING: This will delete all conversations from the database.")
    
    vector_store = VectorStore()
    if vector_store.reset_database():
        print("Database reset successfully.")
    else:
        print("Failed to reset database.")

if __name__ == "__main__":
    main()
