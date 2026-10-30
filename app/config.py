import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()      # reads .env file into the environment


MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:1b")
NUM_CTX = int(os.getenv("NUM_CTX", "1024"))
KEEP_ALIVE = "30m"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

WRITER_TEMPERATURE = float(os.getenv("WRITER_TEMPERATURE", "0.3"))
WRITER_MAX_TOKENS = int(os.getenv("WRITER_MAX_TOKENS", "450"))

JSON_MAX_TOKENS = int(os.getenv("JSON_MAX_TOKENS", "300"))
JSON_TEMPERATURE = float(os.getenv("JSON_TEMPERATURE", "0"))

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT/ "data"
OUTPUT_DIR = ROOT/ "outputs"

#Secrets
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

PASS_SCORE = float(os.getenv("PASS_SCORE", "0.7"))
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "1"))