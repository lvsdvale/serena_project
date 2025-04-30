"""
This file implements the function that returns a prompt template for user interaction.
"""

from langchain_core.prompts import PromptTemplate


def user_interaction_prompt() -> PromptTemplate:
    """
    Creates a prompt template for assisting elderly users based on their prescriptions.

    Returns:
        PromptTemplate: A LangChain prompt template customized for elderly assistance.
    """
    user_interaction_template = """{user_interaction_data} e essa é a minha prescrição médica {prescriptions}.
    """

    user_interaction_prompt_template = PromptTemplate(
        input_variables=["user_interaction_data", "prescriptions"],
        template=user_interaction_template,
    )

    return user_interaction_prompt_template
