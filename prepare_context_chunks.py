# File: create_context_chunks.py

import json
import logging
from typing import List, Dict, Any

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Data Definitions ---
ACRONYM_DEFINITIONS = {
    "DOP": "Delegation of Powers (DoP) refers to the authority granted to various officials within NEEPCO to make decisions and sanction expenditures within defined limits, ensuring efficient operations and accountability.",
    "D(T)": "Director (Technical) is a key role within NEEPCO, responsible for overseeing technical operations and projects.",
    "GM": "General Manager is a managerial position within NEEPCO, with defined approval authorities.",
    "CGM": "Chief General Manager is a senior managerial position in NEEPCO.",
    "ED": "Executive Director is a senior executive role within NEEPCO with significant powers.",
    "CMD": "Chairman cum Managing Director is the highest executive authority in NEEPCO.",
    "BOD": "Board of Directors (BOD) is the governing body of NEEPCO.",
    "HOP": "Head of Project is a role responsible for managing a specific project.",
    "HOD": "Head of Department is a role responsible for a specific functional department.",
    "OEM": "Original Equipment Manufacturer."
}

# --- Helper Functions ---
def format_powers_for_display(data: Dict) -> str:
    """Formats a dictionary of powers into a readable multi-line string."""
    if not isinstance(data, dict):
        return str(data)
    return "\n".join([f"- {key}: {value if value else 'NIL'}" for key, value in data.items()])

# --- Main Processing Function ---
def create_context_chunks_improved(context_file_path: str, output_file_path: str):
    """
    Processes a JSONL context file into a structured and granular JSON chunk file.
    """
    logger.info(f"Starting improved chunk creation from {context_file_path}...")
    chunks = []
    generated_ids = set()

    for acronym, definition in ACRONYM_DEFINITIONS.items():
        chunk_id = f"definition_{acronym}"
        if chunk_id not in generated_ids:
            chunks.append({
                'text': f"Definition: {acronym} stands for {definition}",
                'metadata': {'type': 'definition', 'term': acronym, 'source': 'NEEPCO Policies'},
                'id': chunk_id
            })
            generated_ids.add(chunk_id)

    with open(context_file_path, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            section = data.get('section', '')
            title = data.get('title', '')
            clause = str(data.get('clause', '') or data.get('Clause', ''))
            base_prefix = f"Regarding Section {section}, Title '{title}', Clause {clause}"

            if data.get('remarks_cement'):
                chunk_id = f"policy_cement_sec_{section}_clause_{clause}"
                policy_text = f"{base_prefix} - Policy on Cement Procurement:\n\n"
                policy_text += "\n".join([f"- {item}" for item in data['remarks_cement']])
                chunks.append({
                    'text': policy_text,
                    'metadata': {'section': section, 'title': title, 'clause': clause, 'type': 'policy_detail', 'subject': 'cement'},
                    'id': chunk_id
                })
                generated_ids.add(chunk_id)

            if data.get('remarks_steel'):
                chunk_id = f"policy_steel_sec_{section}_clause_{clause}"
                policy_text = f"{base_prefix} - Policy on Steel Procurement:\n\n"
                policy_text += "\n".join([f"- {item}" for item in data['remarks_steel']])
                chunks.append({
                    'text': policy_text,
                    'metadata': {'section': section, 'title': title, 'clause': clause, 'type': 'policy_detail', 'subject': 'steel'},
                    'id': chunk_id
                })
                generated_ids.add(chunk_id)

            if 'subclauses' in data:
                for subclause in data['subclauses']:
                    sub_id = str(subclause.get('id', ''))
                    sub_desc = subclause.get('description', '') or subclause.get('title', '')
                    chunk_text = f"{base_prefix}\nSub-clause {sub_id}: {sub_desc}"

                    if 'delegation' in subclause:
                        chunk_text += "\n\nDelegation of Powers:\n"
                        chunk_text += format_powers_for_display(subclause['delegation'])

                    if 'methods' in subclause:
                        for method in subclause['methods']:
                            method_name = method.get('method', '')
                            chunk_text += f"\n\nMethod: {method_name}\n"
                            chunk_text += "Delegation of Powers:\n"
                            chunk_text += format_powers_for_display(method['delegation'])
                    
                    remarks_ref = subclause.get('remarks_reference')
                    if remarks_ref:
                         chunk_text += f"\n\nRemarks Reference: {remarks_ref}"

                    chunk_id = f"sec_{section}_clause_{clause}_sub_{sub_id}_{i}"
                    if chunk_id not in generated_ids:
                        chunks.append({
                            'text': chunk_text.strip(),
                            'metadata': {'section': section, 'title': title, 'clause': f"{clause}.{sub_id}", 'type': 'subclause'},
                            'id': chunk_id
                        })
                        generated_ids.add(chunk_id)

    with open(output_file_path, "w", encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Created {len(chunks)} context chunks in {output_file_path}")

# --- Execution Block ---
if __name__ == "__main__":
    # Assumes the uploaded file is named 'combined_context.jsonl' in the same directory
    input_file = "/kaggle/input/dop-dataset/Context/combined_context.jsonl"
    output_file = "/kaggle/working/processed_chunks.json"
    create_context_chunks_improved(input_file, output_file)