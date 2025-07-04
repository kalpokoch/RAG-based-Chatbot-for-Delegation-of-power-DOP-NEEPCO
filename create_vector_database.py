import json
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class PolicyVectorDB:
    def __init__(self, db_path="./chroma_db"):
        """Initialize vector database for policy chunks"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = "neepco_dop_policies"
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print("Loaded existing collection")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "NEEPCO DOP Policy chunks"}
            )
            print("Created new collection")

    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """Remove nested metadata (dicts/lists) and stringify others"""
        flat_meta = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                continue  # skip nested fields
            if isinstance(value, (str, int, float, bool)) or value is None:
                flat_meta[key] = value
            else:
                flat_meta[key] = str(value)  # fallback to string
        return flat_meta

    def add_chunks(self, chunks: List[Dict]):
        """Add policy chunks to vector database"""
        print(f"Adding {len(chunks)} chunks to database...")

        texts = [chunk['text'] for chunk in chunks]
        metadatas = [self._flatten_metadata(chunk['metadata']) for chunk in chunks]
        ids = [chunk['id'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print("Successfully added chunks to database!")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant policy chunks"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return search_results


def setup_vector_database():
    """Complete setup of vector database"""
    
    # Load processed chunks
    with open("processed_chunks.json", "r", encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Initialize database
    vector_db = PolicyVectorDB()
    
    # Add chunks to database
    vector_db.add_chunks(chunks)
    
    return vector_db


# Example usage
if __name__ == "__main__":
    # Setup database
    db = setup_vector_database()
    
    # Test search
    query = "Who approves resignation for executives E-7 and above?"
    results = db.search(query, top_k=2)
    
    print(f"\nQuery: {query}")
    print("Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Relevance: {result['relevance_score']:.3f}")
        print(f"Section: {result['metadata'].get('section', 'N/A')}")
        print(f"Authority: {result['metadata'].get('authority', 'N/A')}")
        print(f"Text: {result['text'][:200]}...")
