"""This file contains config files for api calls"""

import os
import sys

from dotenv import load_dotenv
from langchain.llms import LlamaCpp

load_dotenv()

model_path = os.path.join(
    os.path.dirname(__file__), "models", "Nous-Hermes-2-Mistral-7B-DPO.Q4_K_M.gguf"
)

llm = LlamaCpp(
    model_path=model_path,
    n_ctx=4096,
    n_threads=8,
    temperature=0.7,
    top_p=0.95,
    stop=["</s>", "User:", "Assistant:"],
    verbose=True,
)


device_id = "SERENA001"
