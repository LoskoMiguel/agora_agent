from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
import json

from supabase_utils.connection import get_db_connection
from supabase_utils.db_pool import db as langchain_db
from prompts.prompt_agent import create_profile_prompt, AGENT_CHECK_DB

load_dotenv()

# Using a more recent and standard model
llm = ChatOpenAI(
    model="gpt-4.1",
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0
)

# 1. State Definition
class AgentState(TypedDict):
    instructions: str
    profile: str
    final_message: str

# 2. Tools
@tool
def get_instructions_from_db():
    """Gets instructions from the database on how to create a distinctive profile."""
    print("---OBTENIENDO INSTRUCCIONES DE LA DB---")
    agent_executor = create_react_agent(llm, [langchain_db.run])
    initial_input = AGENT_CHECK_DB
    response = agent_executor.invoke({"messages": [("user", initial_input)]})
    instructions = response['messages'][-1].content
    print(f"Instrucciones generadas (primeros 100 chars): {instructions[:100]}...")
    return instructions

@tool
def create_profile(instructions: str) -> str:
    """Crea un perfil de usuario en formato JSON según las instrucciones"""
    print("---CREANDO PERFIL---")
    user_prompt = (
        "Create the profile as a single JSON object based on the provided schema. "
        "The JSON keys MUST be in snake_case. "
        "Only output the JSON object itself, with no additional text or markdown. "
        "Following the next instructions: " + instructions
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", create_profile_prompt),
        ("user", user_prompt)
    ])
    response = llm.invoke(prompt.format_messages(last_instruction=instructions))
    profile_json = response.content
    print(f"Generated profile: {profile_json}")
    return profile_json

@tool
def add_profile_db(profile: str):
    """Inserta el perfil en la base de datos usando psycopg2."""
    print("---AÑADIENDO PERFIL A LA DB CON PSYCOPG2---")
    try:
        profile_data = json.loads(profile)
    except Exception as e:
        error_message = f"Error al parsear el perfil JSON: {e}. Perfil recibido: {profile}"
        print(error_message)
        return error_message

    # Sanitize keys from the dictionary to be valid column names
    # e.g. "Languages Known" -> "languages_known"
    sanitized_data = {k.lower().replace(" ", "_"): v for k, v in profile_data.items()}

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        keys = ', '.join(sanitized_data.keys())
        placeholders = ', '.join(['%s'] * len(sanitized_data))
        values = tuple(sanitized_data.values())

        insert_query = f"INSERT INTO agents ({keys}) VALUES ({placeholders})"
        
        print(f"Executing query: {insert_query}")
        print(f"With values: {values}")

        cursor.execute(insert_query, values)
        connection.commit()
        
        message = "Perfil insertado correctamente en la base de datos."
        print(message)
        return message

    except Exception as e:
        error_message = f"ERROR EN BASE DE DATOS: {e}"
        print(error_message)
        if connection:
            connection.rollback()
        return error_message
    finally:
        if connection:
            cursor.close()
            connection.close()

# 3. Graph Nodes (calling tools directly)
def get_instructions_node(state: AgentState):
    print("---NODO: OBTENER INSTRUCCIONES---")
    instructions = get_instructions_from_db.invoke({})
    return {"instructions": instructions}

def create_profile_node(state: AgentState):
    print("---NODO: CREAR PERFIL---")
    profile_json = create_profile.invoke({"instructions": state['instructions']})
    return {"profile": profile_json}

def add_profile_db_node(state: AgentState):
    print("---NODO: AÑADIR PERFIL A DB---")
    final_message = add_profile_db.invoke({"profile": state['profile']})
    return {"final_message": final_message}

# 4. Graph Definition
workflow = StateGraph(AgentState)

workflow.add_node("get_instructions", get_instructions_node)
workflow.add_node("create_profile", create_profile_node)
workflow.add_node("add_profile_to_db", add_profile_db_node)

workflow.set_entry_point("get_instructions")
workflow.add_edge("get_instructions", "create_profile")
workflow.add_edge("create_profile", "add_profile_to_db")
workflow.add_edge("add_profile_to_db", END)

app = workflow.compile()

# 5. Execution
initial_state = {
    "instructions": "",
    "profile": "",
    "final_message": ""
}

print("Iniciando el flujo de trabajo...")
for step in app.stream(initial_state, {"recursion_limit": 10}):
    if not step:
        continue
    node_name = list(step.keys())[0]
    state = list(step.values())[0]
    print(f"\n=== Salida del Nodo: {node_name} ===")
    if node_name == "get_instructions":
        print(f"   - instructions: {state.get('instructions', '')[:200]}...")
    elif node_name == "create_profile":
        print(f"   - profile: {state.get('profile', '')}")
    elif node_name == "add_profile_to_db":
        print(f"   - final_message: {state.get('final_message', '')}")
print("\nFlujo de trabajo finalizado.")