import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from typing import List, Dict

class NEEPCOPhi2FineTuner:
    def __init__(self, model_name="microsoft/phi-2"):
        """Initialize fine-tuner for Phi-2 with NEEPCO dataset"""
        
        print("Loading Phi-2 for fine-tuning...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Add padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id
    
    def load_dataset(self, dataset_path: str) -> List[Dict]:
        """Load and prepare NEEPCO dataset"""
        
        data = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line.strip())
                data.append(item)
        
        print(f"Loaded {len(data)} training examples")
        return data
    
    def format_training_data(self, data: List[Dict]) -> List[str]:
        """Format data for Phi-2 training"""
        
        formatted_data = []
        
        for item in data:
            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output = item.get('output', '')
            
            # Create training prompt
            if input_text:
                prompt = f"""You are a helpful assistant for NEEPCO's Delegation of Power policies.

Question: {instruction}
Context: {input_text}
Answer: {output}{self.tokenizer.eos_token}"""
            else:
                prompt = f"""You are a helpful assistant for NEEPCO's Delegation of Power policies.

Question: {instruction}
Answer: {output}{self.tokenizer.eos_token}"""
            
            formatted_data.append(prompt)
        
        return formatted_data
    
    def tokenize_data(self, texts: List[str]) -> Dataset:
        """Tokenize training data"""
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'], 
                truncation=True, 
                padding=True, 
                max_length=512,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_dict({"text": texts})
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def fine_tune(self, dataset_path: str, output_dir: str = "./neepco_phi2_finetuned"):
        """Complete fine-tuning process"""
        
        print("Starting fine-tuning process...")
        
        # Load and format data
        raw_data = self.load_dataset(dataset_path)
        formatted_texts = self.format_training_data(raw_data)
        tokenized_dataset = self.tokenize_data(formatted_texts)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",
            learning_rate=5e-5,
            fp16=True,
            remove_unused_columns=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # Start training
        print("Training started...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Fine-tuning complete! Model saved to {output_dir}")
        return output_dir

# Updated RAG chatbot to use fine-tuned model
class NEEPCOPolicyChatbotFineTuned:
    def __init__(self, finetuned_model_path, vector_db_path="./chroma_db"):
        """Initialize RAG chatbot with fine-tuned Phi-2"""
        
        print("Loading fine-tuned Phi-2 model...")
        self.tokenizer = AutoTokenizer.from_pretrained(finetuned_model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            finetuned_model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print("Loading vector database...")
        from create_vector_database import PolicyVectorDB
        self.vector_db = PolicyVectorDB(vector_db_path)
        
        print("Fine-tuned chatbot ready!")
    
    def chat(self, query: str) -> Dict:
        """RAG pipeline with fine-tuned model"""
        
        # Retrieve context (same as before)
        context_results = self.vector_db.search(query, top_k=2)
        
        # Format prompt for fine-tuned model
        context_text = ""
        for result in context_results:
            context_text += f"Policy: {result['text']}\n"
        
        prompt = f"""You are a helpful assistant for NEEPCO's Delegation of Power policies.

{context_text}
Question: {query}
Answer:"""
        
        # Generate with fine-tuned model
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1000)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids.to(self.model.device),
                attention_mask=inputs.attention_mask.to(self.model.device),
                max_length=len(inputs.input_ids[0]) + 200,
                do_sample=True,
                temperature=0.1,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response[len(prompt):].strip()
        
        return {
            'question': query,
            'answer': answer,
            'sources': [{'section': r['metadata']['section'], 
                        'authority': r['metadata']['authority']} for r in context_results]
        }

# Complete workflow
def complete_workflow():
    """Complete workflow: Fine-tune + RAG"""
    
    print("=== NEEPCO DOP Complete Workflow ===")
    
    # Step 1: Fine-tune Phi-2 with your dataset
    print("\n1. Fine-tuning Phi-2...")
    fine_tuner = NEEPCOPhi2FineTuner()
    model_path = fine_tuner.fine_tune("Dataset/combined_dataset.jsonl")
    
    # Step 2: Setup RAG with fine-tuned model
    print("\n2. Setting up RAG with fine-tuned model...")
    chatbot = NEEPCOPolicyChatbotFineTuned(model_path)
    
    # Step 3: Test
    print("\n3. Testing complete system...")
    test_queries = [
        "Who approves resignation for executives E-7 and above?",
        "What is the authority for study leave?",
        "Who can form interview panels?"
    ]
    
    for query in test_queries:
        response = chatbot.chat(query)
        print(f"\nQ: {query}")
        print(f"A: {response['answer']}")
        print(f"Sources: {len(response['sources'])} sections")

if __name__ == "__main__":
    # Run complete workflow
    complete_workflow()