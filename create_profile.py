from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from dotenv import load_dotenv
import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser

from supabase_utils.connection import get_db_connection
from supabase_utils.db_pool import db as langchain_db
from prompts.prompt_agent import create_profile_prompt, AGENT_CHECK_DB
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph_swarm import create_swarm, create_handoff_tool
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Using a more recent and standard model
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0
)

@tool
def transfer_instructions_db(instructions: str):
    """ Transferir el control al agente de la creacion de perfil junto con las instrucciones """
    return {
        "__handoff__": {
            "to": "create_profile_agent",
            "update": {
                "instructions": instructions
            }
        }
    }


@tool
def transfer_profile_to_db(profile: str):
    """Transfiere el perfil generado al agente que lo inserta en la base de datos"""
    return {
        "__handoff__": {
            "to": "add_profile_db_agent",
            "update": {
                "profile": profile
            }
        }
    }

@tool
def instruction_db():
    """ Esta tool es para enviar instrucciones al agente de creacion de perfil """
    print("INICIANDO INSTRUCION_DB")
    sql_toolkit = SQLDatabaseToolkit(db=langchain_db, llm=llm)
    tools = sql_toolkit.get_tools()

    agent_executor = create_react_agent(
        llm,
        tools,
    )

    initial_input = AGENT_CHECK_DB
    response = agent_executor.invoke({"messages": [("user", initial_input)]})

    agent_outcome = ""
    if response and response['messages'] and isinstance(response['messages'][-1], AIMessage):
        agent_outcome = response['messages'][-1].content

    return {"instructions": agent_outcome}


@tool
def create_profile(instructions: str) -> str:
    """Crea un perfil de usuario en formato JSON según las instrucciones"""
    print("INICIANDO CREACION DE PERFIL")

    user_prompt = (
        "Create the profile as a single JSON object based on the provided schema. "
        "Only output the JSON object itself, with no additional text or markdown. "
        "Following the next instructions: " + instructions
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", create_profile_prompt),
        ("user", user_prompt)
    ])

    response = llm.invoke(prompt.format_messages(last_instruction=instructions))

    profile = response.content

    print(f"Generated profile: {profile}")
    return profile

@tool
def add_profile_db(profile: str):
    "Inserta el perfil en la base de datos. El perfil es un JSON"
    print("INICIANDO ADICION DE PERFIL A LA BASE DE DATOS")

    import json
    try:
        profile_data = json.loads(profile)
    except Exception as e:
        print("Error al parsear el perfil JSON:", e)
        return f"Error al parsear el perfil JSON: {e}"

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if isinstance(profile_data, dict):
            profile_data = [profile_data]  # lo hacemos lista

        keys = ', '.join(profile_data[0].keys())
        placeholders = ', '.join(['%s'] * len(profile_data[0]))

        for item in profile_data:
            cursor.execute(f"INSERT INTO agents ({keys}) VALUES ({placeholders})", tuple(item.values()))
        connection.commit()

    except Exception as e:
        print("ERROR EN BASE DE DATOS:", e)
        connection.rollback()
        return f"Error en base de datos: {e}"

    finally:
        cursor.close()
        connection.close()

    return "Perfil insertado correctamente en la base de datos."

agent_instruction_db = create_react_agent(
    name="instruction_db_agent",
    model=llm,
    tools=[instruction_db, transfer_instructions_db],
    prompt="Eres un agente que recibe instrucciones para crear un perfil de usuario. Debes seguir las instrucciones al pie de la letra y transferir el control al agente de creacion de perfil."
)

agent_create_profile = create_react_agent(
    name="create_profile_agent",
    model=llm,
    tools=[create_profile, transfer_profile_to_db],
    prompt="""
Eres un agente que crea perfiles de usuario siguiendo instrucciones dadas. 
Usa la herramienta `create_profile` para generar un perfil en formato JSON.

Después, **usa inmediatamente** la herramienta `transfer_profile_to_db` para transferir ese perfil generado al siguiente agente, quien lo insertará en la base de datos.

Nunca devuelvas el JSON directamente. Tu tarea es:
1. Generar el perfil con `create_profile`.
2. Enviarlo con `transfer_profile_to_db`.
"""
)

agent_add_profile_db = create_react_agent(
    name="add_profile_db_agent",
    model=llm,
    tools=[add_profile_db],
    prompt="Eres un agente que inserta el perfil de usuario en la base de datos. Debes seguir las instrucciones proporcionadas y agregar el perfil a la base de datos."
)

# Swarm
swarm = create_swarm(
    agents=[
        agent_instruction_db,
        agent_create_profile,
        agent_add_profile_db
    ],
    default_active_agent="instruction_db_agent"
).compile()

def pretty_print(chunk: dict):
    for agent_name, agent_data in chunk.items():
        print(f"\n=== 📡 Agente activo: {agent_name} ===")
        for message in agent_data["messages"]:
            if isinstance(message, AIMessage):
                if message.content:
                    print(f"🤖 AI: {message.content}")
            elif isinstance(message, ToolMessage):
                print(f"🛠 Resultado herramienta: {message.content}")

initial_state = {
    "messages": [
        {
            "role": "user",
            "content": "Create a random profile"
        }
    ],
    "instructions": "",
    "profile": ""
}

for chunk in swarm.stream(initial_state):
    pretty_print(chunk)