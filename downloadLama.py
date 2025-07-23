from transformers import AutoModelForCausalLM, AutoTokenizer
import os

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
local_dir = "./tinyllama_local" # This is where the model files will be saved

# Create the directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

print(f"Downloading tokenizer for {model_id} to {local_dir}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.save_pretrained(local_dir)
print("Tokenizer downloaded.")

print(f"Downloading model for {model_id} to {local_dir}...")
# You might want to specify a torch_dtype here depending on your GPU,
# e.g., torch_dtype=torch.float16 or torch.bfloat16 for faster download/smaller size
model = AutoModelForCausalLM.from_pretrained(model_id)
model.save_pretrained(local_dir)
print("Model downloaded.")

print(f"\nModel and tokenizer files saved locally in: {os.path.abspath(local_dir)}")
print("You can now find files like config.json, tokenizer.json, and model.safetensors (or pytorch_model.bin) in this directory.")