import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Use OpenAI-compatible client for Groq
# Groq's SDK provides `groq.AsyncGroq` but we can use `openai` client with base_url
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1"),
)

# Fetch and print model IDs
models = client.models.list()
for m in models.data:
    print(m.id)
