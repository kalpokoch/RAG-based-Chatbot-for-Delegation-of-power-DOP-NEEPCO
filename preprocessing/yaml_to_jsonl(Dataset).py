import yaml
import json
from pathlib import Path

# Set your dataset directory path here
input_dir = Path(r"D:\GitHub\RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO\Dataset")
output_file = input_dir / "combined_dataset.jsonl"

yaml_files = list(input_dir.glob("*.yaml"))

if not yaml_files:
    print("❌ No YAML files found in the given directory.")
    exit()

with open(output_file, "w", encoding="utf-8") as out_file:
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, list):
                    print(f"⚠️ Skipping {yaml_file.name} — expected a list of records.")
                    continue
                for item in data:
                    out_file.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"✅ Processed: {yaml_file.name}")
        except Exception as e:
            print(f"❌ Error reading {yaml_file.name}: {e}")

print(f"\n✅ Combined JSONL created at: {output_file.resolve()}")
