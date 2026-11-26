from pydantic_ai import LLM, Prompt
# Simple sanity check – a dummy prompt that should echo back
prompt = Prompt("Say hello in Portuguese.")
response = LLM().complete(prompt)
print(response)   # → "Olá"