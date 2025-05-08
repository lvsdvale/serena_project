"""Implements user interaction agent"""

import os
import sys

from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatOllama

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from llm_interactions.tools.get_diagnoses_tool import get_diagnoses_by_device
from llm_interactions.tools.get_prescripiton_tool import \
    get_prescriptions_by_device
from llm_interactions.tools.log_interaction_tool import log_interaction

llm = ChatOllama(model="tinyllama", temperature=0)

tools = [
    get_prescriptions_by_device,
    log_interaction,
    get_diagnoses_by_device,
]

user_interaction_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
