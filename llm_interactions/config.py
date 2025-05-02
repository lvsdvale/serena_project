"""This file contains config files for api calls"""

import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
)
