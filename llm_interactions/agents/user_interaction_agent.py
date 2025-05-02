"""This file implements user_interaction_agent that will be used"""

import os
import sys

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_huggingface import HuggingFaceEndpoint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)
from dotenv import load_dotenv

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
)

user_interaction_data = "estou com dor de cabeça"
prescription = "em caso de dor de cabeça tomar paracetamol"
chain = llm
res = chain.invoke(
    input={
        "user_interaction_data": user_interaction_data,
        "prescriptions": prescription,
    }
)
print(res)
