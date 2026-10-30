"""Create Ollama chat models from the current runtime configuration."""

from langchain_ollama import ChatOllama
from app import config


def _shared_options() -> dict:
    # Read MODEL_NAME each time so changing it in the Settings screen takes effect
    # without restarting the FastAPI process.
    return {
        "model": config.MODEL_NAME,
        "base_url": config.OLLAMA_BASE_URL,
        "num_ctx": config.NUM_CTX,
        "keep_alive": config.KEEP_ALIVE,
    }


def get_json_model():
    return ChatOllama(
        **_shared_options(),
        temperature=config.JSON_TEMPERATURE,
        num_predict=config.JSON_MAX_TOKENS,
        format="json",
    )


def get_writer_model():
    return ChatOllama(
        **_shared_options(),
        temperature=config.WRITER_TEMPERATURE,
        num_predict=config.WRITER_MAX_TOKENS,
    )
