from dotenv import load_dotenv
import os
from llama_index.core import VectorStoreIndex, Document,  SimpleDirectoryReader
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.schema.messages import SystemMessage
from langchain.agents import AgentExecutor,initialize_agent, Tool
from langchain.agents.agent_toolkits import create_retriever_tool,create_conversational_retrieval_agent
from langchain.prompts import MessagesPlaceholder
from langchain_fireworks import Fireworks 
from llama_index.core.langchain_helpers.agents import (
    IndexToolConfig,
    LlamaIndexTool,
)
from llama_index.core import StorageContext, load_index_from_storage
from searchPlaces import SearchNearbyPlacesTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from fastapi import FastAPI
from fastapi import Header, HTTPException, Depends

from pydantic import BaseModel, confloat

class LocationStepCount(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
    step_count: int

app = FastAPI()


# Load environment variables from .env
load_dotenv()

llm = ChatOpenAI(temperature=0
                 ,model="gpt-4")

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="index")

# load index
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

# Create conversation chain that uses our vectordb as retriver, this also allows for chat history management

tool_config = IndexToolConfig(
    query_engine=query_engine,
    name=f"mental_health_tool",
    description=f"Useful when you want to search information regarding good habits",
)

reterieval_tool = LlamaIndexTool.from_tool_config(tool_config)
tools = [reterieval_tool,SearchNearbyPlacesTool()]

memory_key = "history"
memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
              You are TouchGrass, you are the user's friend but you also frequently act as their therapist.
              They'll give you information about their latitude, longitude, schedule, and their number of steps today.
              You should use the mental_health_tool to give appropriate advice and inform what places they should go.
              You can and find places for them to go using the SearchNearbyPlaces tool you should infer the types of places they should go based on the information from the mental_health_tool.
              You should recommend several places and activities to go based on your information and potential times.
""",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True,
                                   return_intermediate_steps=True)

while True:
    user_input = input("Type your message (type 'exit' to quit): ")
    
    if user_input.lower() == 'exit':
        break  # exit the loop if the user types 'exit'
    
    result = agent_executor({"input": user_input})
    
    print("Agent Output:", result['output'])