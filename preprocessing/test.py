import yaml
import json
from pathlib import Path

input_dir = Path(r"D:\GitHub\RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO\Context")
output_file = input_dir / "combined_context.jsonl"

def safe_json_dumps(obj, ensure_ascii=False):
    """Safely serialize objects to JSON with detailed error reporting"""
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii)
    except Exception as e:
        print(f"      ❌ JSON serialization error: {e}")
        print(f"      📋 Problematic object keys: {list(obj.keys()) if isinstance(obj, dict) else 'Not a dict'}")
        
        # Try to identify the problematic field
        if isinstance(obj, dict):
            for key, value in obj.items():
                try:
                    json.dumps({key: value}, ensure_ascii=ensure_ascii)
                except:
                    print(f"      🔍 Problematic field: '{key}' = {type(value)}")
                    if isinstance(value, (dict, list)):
                        print(f"         Content preview: {str(value)[:200]}...")
        
        # Return a safe version
        return json.dumps({"error": f"Serialization failed: {str(e)}", "original_keys": list(obj.keys()) if isinstance(obj, dict) else None}, ensure_ascii=ensure_ascii)

def process_clause_detailed(clause_data, section_meta, clause_index):
    """Process a single clause with detailed logging"""
    print(f"      🔍 Processing clause {clause_index}: {clause_data.get('clause', 'Unknown')}")
    print(f"         Title: {clause_data.get('title', 'No title')[:60]}...")
    
    entries = []
    
    try:
        # Check if clause has subclauses
        if 'subclauses' in clause_data and clause_data['subclauses']:
            print(f"         📝 Found {len(clause_data['subclauses'])} subclauses")
            base_clause = {k: v for k, v in clause_data.items() if k != 'subclauses'}
            
            for i, subclause in enumerate(clause_data['subclauses']):
                print(f"            Processing subclause {i+1}: {subclause.get('id', 'Unknown')}")
                
                entry = {
                    **section_meta,
                    **base_clause,
                    **subclause
                }
                entries.append(entry)
        else:
            print(f"         📝 No subclauses, processing as single entry")
            entry = {
                **section_meta,
                **clause_data
            }
            entries.append(entry)
            
        print(f"         ✅ Successfully created {len(entries)} entries")
        return entries
        
    except Exception as e:
        print(f"         ❌ Error processing clause: {e}")
        # Return a minimal safe entry
        return [{
            **section_meta,
            "clause": clause_data.get('clause', 'unknown'),
            "title": clause_data.get('title', 'Error processing clause'),
            "error": str(e)
        }]

yaml_files = sorted(input_dir.glob("*.yaml"))

with open(output_file, "w", encoding="utf-8") as out_file:
    for yaml_file in yaml_files:
        print(f"\n📋 Processing: {yaml_file.name}")
        
        # Focus on Section I for debugging
        if "Section_I" not in yaml_file.name:
            print(f"   ⏭️ Skipping for now, focusing on Section I")
            continue
            
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            
            if isinstance(data, dict) and "clauses" in data:
                section_meta = {k: v for k, v in data.items() if k != "clauses"}
                print(f"   📝 Section: {section_meta.get('section', 'Unknown')}")
                print(f"   🔢 Found {len(data['clauses'])} clauses to process")
                
                entries_added = 0
                
                # Process each clause with detailed logging
                for i, clause in enumerate(data['clauses'], 1):
                    clause_entries = process_clause_detailed(clause, section_meta, i)
                    
                    # Write each entry with error handling
                    for j, entry in enumerate(clause_entries):
                        try:
                            json_line = safe_json_dumps(entry, ensure_ascii=False)
                            out_file.write(json_line + "\n")
                            entries_added += 1
                        except Exception as write_error:
                            print(f"         ❌ Failed to write entry {j+1}: {write_error}")
                
                print(f"   ✅ Total entries written: {entries_added}")
                
        except Exception as e:
            print(f"   ❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()

print(f"\n✅ Processing complete. Check output file: {output_file}")
