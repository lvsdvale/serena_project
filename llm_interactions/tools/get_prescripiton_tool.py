"""This file implements the get prescription tool"""

from langchain_core.tools import Tool

get_prescription_tool = Tool(
    name="get prescription tool",
    func="?",
    description="useful when you need to get the prescription",
)
