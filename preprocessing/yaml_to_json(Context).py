import yaml
import json
from pathlib import Path

# ————————————————————————————————
# Update this to point at your Context directory
input_dir = Path(r"D:\GitHub\RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO\Context")
# The merged output file
output_file = input_dir / "combined_context.jsonl"
# ————————————————————————————————

yaml_files = sorted(input_dir.glob("*.yaml"))

if not yaml_files:
    print("❌ No YAML files found in the given directory:", input_dir)
    exit(1)

with open(output_file, "w", encoding="utf-8") as out_file:
    for yaml_file in yaml_files:
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))

            # ✅ If the top-level is a dict with section metadata and clauses
            if isinstance(data, dict) and "clauses" in data:
                section_meta = {k: v for k, v in data.items() if k != "clauses"}
                for clause in data["clauses"]:
                    enriched_clause = {**section_meta, **clause}
                    out_file.write(json.dumps(enriched_clause, ensure_ascii=False) + "\n")
                print(f"✅ Processed (with section metadata): {yaml_file.name}")

            # ✅ If the top-level is already a list
            elif isinstance(data, list):
                for item in data:
                    out_file.write(json.dumps(item, ensure_ascii=False) + "\n")
                print(f"✅ Processed (flat list): {yaml_file.name}")

            else:
                print(f"⚠️ Skipping {yaml_file.name} — unrecognized format.")

        except Exception as e:
            print(f"❌ Error reading {yaml_file.name}: {e}")

print(f"\n✅ Combined JSONL created at: {output_file.resolve()}")
