"""This file contains config files for api calls"""

import os
import sys

from dotenv import load_dotenv
from langchain.chat_models import ChatHuggingFace
from langchain.llms import HuggingFaceHub, LlamaCpp
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_path = os.path.join(
    os.path.dirname(__file__), "models", "Nous-Hermes-2-Mistral-7B-DPO.Q4_K_M.gguf"
)
"""
llm = LlamaCpp(
    model_path=model_path,
    n_ctx=1024,
    n_threads=8,
    temperature=0.7,
    top_p=0.95,
    stop=["</s>", "User:", "Assistant:"],
    chat_format="chatml",
    verbose=False,
    use_mlock=True,
    f16_kv=True,
    n_batch=512,
)
"""
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


device_id = "SERENA001"
