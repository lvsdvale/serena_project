"""This file contains config files for api calls"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
api_email = os.getenv("email")
api_password = os.getenv("password")
device_id = os.getenv("device_id")