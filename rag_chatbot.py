import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from create_vector_database import PolicyVectorDB
import json
from typing import List, Dict

class NEEPCOPolicyChatbot:
    def __init__(self, model_path="Model/phi-2", vector_db_path="./chroma_db"):
        """Initialize the RAG chatbot"""
        
        print("Loading Phi-2 model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            torch_dtype=torch.float16,
            trust_remote_code=True,
            device_map="auto"
        )
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("Loading vector database...")
        self.vector_db = PolicyVectorDB(vector_db_path)
        
        print("Chatbot ready!")
    
    def retrieve_context(self, query: str, top_k: int = 2) -> List[Dict]:
        """Retrieve relevant policy context for the query"""
        return self.vector_db.search(query, top_k=top_k)
    
    def format_prompt(self, query: str, context_results: List[Dict]) -> str:
        """Format the prompt with context and query for Phi-2"""
        
        # Build context section
        context_text = ""
        for i, result in enumerate(context_results, 1):
            context_text += f"Policy {i}:\n"
            context_text += f"Section: {result['metadata']['section']}\n"
            context_text += f"Authority: {result['metadata']['authority']}\n"
            context_text += f"Details: {result['text']}\n\n"
        
        # Create the full prompt
        prompt = f"""You are a helpful assistant for NEEPCO's Delegation of Power (DOP) policies. Use only the provided policy information to answer questions accurately.

Policy Information:
{context_text}

Question: {query}

Answer: Based on the above policy information,"""
        
        return prompt
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """Generate response using Phi-2"""
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1500)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids.to(self.model.device),
                attention_mask=inputs.attention_mask.to(self.model.device),
                max_length=len(inputs.input_ids[0]) + max_length,
                do_sample=True,
                temperature=0.1,  # Low temperature for factual responses
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (after "Answer:")
        answer_start = response.find("Answer: Based on the above policy information,")
        if answer_start != -1:
            answer = response[answer_start + len("Answer: Based on the above policy information,"):].strip()
        else:
            answer = response[len(prompt):].strip()
        
        return answer
    
    def chat(self, query: str) -> Dict:
        """Complete RAG pipeline: retrieve context + generate answer"""
        
        print(f"Processing query: {query}")
        
        # Step 1: Retrieve relevant context
        context_results = self.retrieve_context(query)
        
        # Step 2: Format prompt with context
        prompt = self.format_prompt(query, context_results)
        
        # Step 3: Generate response
        answer = self.generate_response(prompt)
        
        # Step 4: Prepare response with sources
        sources = []
        for result in context_results:
            sources.append({
                'section': result['metadata']['section'],
                'title': result['metadata']['title'],
                'authority': result['metadata']['authority'],
                'relevance': result['relevance_score']
            })
        
        return {
            'question': query,
            'answer': answer,
            'sources': sources,
            'context_used': [r['text'] for r in context_results]
        }

# Simple CLI interface
def main():
    print("Initializing NEEPCO DOP Policy Chatbot...")
    chatbot = NEEPCOPolicyChatbot()
    
    print("\nChatbot ready! Ask questions about NEEPCO's Delegation of Power policies.")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("Your question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Get response
            response = chatbot.chat(query)
            
            print(f"\nAnswer: {response['answer']}")
            print(f"\nSources:")
            for i, source in enumerate(response['sources'], 1):
                print(f"{i}. Section {source['section']} - {source['title']}")
                print(f"   Authority: {source['authority']} (Relevance: {source['relevance']:.2f})")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    main()