import os
from dotenv import load_dotenv
load_dotenv()                       # reads .env in the current working directory
print("OPENAI_API_KEY →", os.getenv("OPENAI_API_KEY")[:8] + "…" if os.getenv("OPENAI_API_KEY") else "None")
print("GEMINI_API_KEY →", os.getenv("GEMINI_API_KEY")[:8] + "…" if os.getenv("GEMINI_API_KEY") else "None")