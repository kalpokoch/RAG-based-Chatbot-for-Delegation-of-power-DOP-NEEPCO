import json
from typing import List, Dict

def create_context_chunks(context_file_path: str) -> List[Dict]:
    """
    Convert your combined_context.jsonl into searchable chunks
    """
    chunks = []
    
    with open(context_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            
            # Create a readable text chunk from structured data
            chunk_text = f"Section {data.get('section', '')}: {data.get('title', '')}\n"
            
            if data.get('clause'):
                chunk_text += f"Clause {data['clause']}: "
            
            # Add extent of power information
            if data.get('extent_of_power'):
                chunk_text += "Powers - "
                for power in data['extent_of_power']:
                    if isinstance(power, dict):
                        for grade, extent in power.items():
                            chunk_text += f"{grade}: {extent}; "
                    else:
                        chunk_text += f"{power}; "
                chunk_text += "\n"
            
            # Add authority information
            if data.get('authority'):
                chunk_text += f"Authority: {data['authority']}\n"
            
            # Add subclauses if present
            if data.get('subclauses'):
                chunk_text += "Subclauses:\n"
                for subclause in data['subclauses']:
                    chunk_text += f"- {subclause.get('id', '')}: {subclause.get('description', '')}\n"
            
            # Add remarks
            if data.get('remarks'):
                chunk_text += f"Remarks: {data['remarks']}\n"
            
            # Create chunk with metadata
            chunk = {
                'text': chunk_text.strip(),
                'metadata': {
                    'section': data.get('section', ''),
                    'title': data.get('title', ''),
                    'clause': data.get('clause', ''),
                    'authority': data.get('authority', ''),
                    'source_data': data  # Keep original for reference
                },
                'id': f"section_{data.get('section', '')}_{data.get('clause', '')}"
            }
            
            chunks.append(chunk)
    
    return chunks

# Example usage
if __name__ == "__main__":
    # Convert your context file
    chunks = create_context_chunks("Context/combined_context.jsonl")
    
    # Save chunks for later use
    with open("processed_chunks.json", "w", encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(chunks)} context chunks")
    print("Sample chunk:")
    print(chunks[0]['text'])