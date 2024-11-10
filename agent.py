import torch
from transformers import pipeline

# model_name = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
# model_name = "Qwen/Qwen2.5-1.5B"
model_name = "google/gemma-2-9b"
download_path = "D:/jarvis-data/agent"

pipe = pipeline(
    "text-generation",
    model=model_name,
    device="cuda",  # replace with "mps" to run on a Mac device
    cache_dir=download_path,
)

text = "Once upon a time,"
outputs = pipe(text, max_new_tokens=256)
response = outputs[0]["generated_text"]
print(response)
