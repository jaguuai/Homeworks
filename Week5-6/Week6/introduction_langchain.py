# -*- coding: utf-8 -*-
"""
LangChain + Neo4j + OpenAI integration demo
Creates an interactive Cypher assistant with LangChain agents and Neo4j memory
Author: alice
"""
import os
from uuid import uuid4
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser

# Neo4j integration for memory and graph access
from langchain_neo4j import Neo4jChatMessageHistory, Neo4jGraph

# Load environment variables (API keys, DB credentials)
load_dotenv(dotenv_path="C:/Users/alice/OneDrive/Masaüstü/LangChainIntrudiction/neo4j.env")

# Generate a unique session ID
SESSION_ID = str(uuid4())
print(f"Session ID: {SESSION_ID}")

# Load OpenAI API key from environment (automatically used by ChatOpenAI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize ChatOpenAI model (e.g., GPT-3.5-turbo)
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo"  # or use "gpt-4" if available
)

# Initialize Neo4j graph for storing chat memory and querying
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Define prompt template for Cypher assistance
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a Neo4j expert having a conversation about how to create Cypher queries."
    ),
    ("human", "{input}")
])


# Create the full LLM pipeline for Cypher chat (prompt → LLM → output parser)
cypher_chat = prompt | llm | StrOutputParser()

# Define memory function to persist conversation in Neo4j
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Define tool that allows agent to use Cypher assistant
tools = [
    Tool.from_function(
        name="Cypher Support",
        description="Use this tool to help generate or debug Cypher queries.",
        func=cypher_chat.invoke,
    )
]

# Load an agent prompt template from LangChain hub
agent_prompt = hub.pull("hwchase17/react-chat")

# Create a ReAct-style agent with tools and LLM
agent = create_react_agent(llm, tools, agent_prompt)

# Wrap agent in an executor to handle function calling
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Enable session-based memory by wrapping the executor
cypher_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Run a CLI loop to allow user interaction in terminal
while (q := input("> ")) != "exit":
    response = cypher_agent.invoke(
        {"input": q},
        {"configurable": {"session_id": SESSION_ID}},
    )
    print(response["output"])