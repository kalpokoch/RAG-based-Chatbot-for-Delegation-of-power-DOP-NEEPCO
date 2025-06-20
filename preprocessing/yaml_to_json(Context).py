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
            if not isinstance(data, list):
                print(f"⚠️ Skipping {yaml_file.name} — expected a list of records at top level.")
                continue
            for item in data:
                out_file.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"✅ Processed: {yaml_file.name}")
        except Exception as e:
            print(f"❌ Error reading {yaml_file.name}: {e}")

print(f"\n✅ Combined JSONL created at: {output_file.resolve()}")
