import os
from openai import OpenAI

# The OpenAI client reads OPENAI_API_KEY and OPENAI_API_BASE from the .env file via load_dotenv
# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
models = client.models.list()
print("Available Groq models for the current key:")
for m in models.data:
    print(m.id)
