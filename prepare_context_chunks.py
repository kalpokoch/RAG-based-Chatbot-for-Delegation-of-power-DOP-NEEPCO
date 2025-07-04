import json
from typing import List, Dict

def create_context_chunks(context_file_path: str) -> List[Dict]:
    """
    Convert your combined_context.jsonl into fine-grained searchable chunks
    Each clause and subclause will become an individual chunk
    """
    chunks = []

    with open(context_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())

            section = data.get('section', '')
            title = data.get('title', '')
            clause = data.get('clause', '')
            authority = data.get('authority', '')
            remarks = data.get('remarks', [])

            # Add main clause chunk if extent_of_power exists
            if data.get('extent_of_power'):
                chunk_text = f"Section {section}: {title}\n"
                if clause:
                    chunk_text += f"Clause {clause}: "

                chunk_text += "Powers - "
                for power in data['extent_of_power']:
                    if isinstance(power, dict):
                        for grade, extent in power.items():
                            chunk_text += f"{grade}: {extent}; "
                    else:
                        chunk_text += f"{power}; "

                chunk_text += f"\nAuthority: {authority}\n"

                if remarks:
                    chunk_text += f"Remarks: {' '.join(str(r) for r in remarks)}"

                chunks.append({
                    'text': chunk_text.strip(),
                    'metadata': {
                        'section': section,
                        'title': title,
                        'clause': clause,
                        'authority': authority,
                    },
                    'id': f"section_{section}_clause_{clause}"
                })

            # Create separate chunks for each subclause
            if data.get('subclauses'):
                for subclause in data['subclauses']:
                    sub_id = subclause.get('id', '')
                    sub_text = subclause.get('description', '')
                    delegation = subclause.get('delegation', {})

                    chunk_text = f"Section {section}: {title}\n"
                    chunk_text += f"Clause {clause}{sub_id}: {sub_text}\n"

                    if delegation:
                        chunk_text += "Delegation - "
                        for grade, power in delegation.items():
                            chunk_text += f"{grade}: {power}; "

                    if remarks:
                        chunk_text += f"\nRemarks: {' '.join(str(r) for r in remarks)}"

                    chunks.append({
                        'text': chunk_text.strip(),
                        'metadata': {
                            'section': section,
                            'title': title,
                            'clause': f"{clause}{sub_id}",
                            'authority': authority,
                        },
                        'id': f"section_{section}_clause_{clause}{sub_id}"
                    })

    return chunks

# Example usage
if __name__ == "__main__":
    chunks = create_context_chunks("/kaggle/input/dop-dataset/Context/combined_context.jsonl")

    with open("processed_chunks.json", "w", encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Created {len(chunks)} context chunks")
    print("Sample chunk:")
    print(chunks[0]['text'])
