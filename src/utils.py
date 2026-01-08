from dotenv import load_dotenv
from functools import lru_cache
import os

from openai import OpenAI


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    load_dotenv()
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
