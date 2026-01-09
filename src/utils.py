from dotenv import load_dotenv
from functools import lru_cache
import logging
import os
from pathlib import Path

from openai import OpenAI


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    load_dotenv()
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@lru_cache(maxsize=1)
def get_logger(logs_dir: Path, logger_name: str) -> logging.Logger:
    # Setup logging
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "snapcitr.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    return logging.getLogger(logger_name)
