from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from supabase_utils.connection import get_db_connection
from supabase_utils.db_pool import db as langchain_db
from prompts.prompt_agent import create_profile_prompt, AGENT_CHECK_DB
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import json
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0.8
)

def get_instructions_from_db():
    """Gets instructions from the database on how to create a distinctive profile."""
    print("---OBTENIENDO INSTRUCCIONES DE LA DB---")
    agent_executor = create_react_agent(llm, [langchain_db.run])
    initial_input = AGENT_CHECK_DB
    response = agent_executor.invoke({"messages": [("user", initial_input)]})
    instructions = response['messages'][-1].content
    print(f"Instrucciones generadas")
    return instructions

def create_profile(instructions: str) -> str:
    """Crea un perfil de usuario en formato JSON según las instrucciones"""
    print("---CREANDO PERFIL---")
    user_prompt = (
        "Create a strategically unique and authentic profile as a single JSON object based on the provided schema. "
        "The JSON keys MUST be in snake_case. "
        "Ensure the profile is distinctive, culturally coherent, and professionally believable. "
        "Only output the JSON object itself, with no additional text or markdown. "
        "Following the comprehensive instructions: " + instructions
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", create_profile_prompt),
        ("user", user_prompt)
    ])
    response = llm.invoke(prompt.format_messages(last_instruction=instructions))
    profile_json = response.content
    print(f"Generated profile: {profile_json}")
    return profile_json

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

add_profile_agent = create_react_agent(
    name="add_profile_agent",
    model=llm,
    prompt=(
        "You are a specialist in creating high-quality social media profiles. "
        "Your process is meticulous and follows these exact steps: "
        "1) FIRST: Use 'get_instructions_from_db' to obtain a detailed analysis of existing profiles and strategic guidelines. "
        "2) SECOND: With those detailed instructions, use 'create_profile' to generate a unique and authentic profile that stands out from common patterns. "
        "3) THIRD: Use 'add_profile_db' to insert the validated profile into the database. "
        "Focus on creating profiles that are distinctive, culturally coherent, and professionally credible. "
        "Never generate generic profiles or ones filled with common clichés."
    ),
    tools=[get_instructions_from_db, create_profile, add_profile_db],
)

supervisor = create_supervisor(
    agents=[add_profile_agent],
    model=llm,
    prompt=(
        "You are the supervisor of an advanced social media profile creation system. "
        "Your goal is to ensure that unique, authentic, and strategically differentiated profiles are generated. "
        "Coordinate the agent to follow the full process: DB analysis → strategic creation → validated insertion. "
        "Demand exceptional quality in every profile generated."
    )
).compile()

print("Create a high-quality, strategically unique profile that stands out from existing patterns")

create = "Create A Profile"

result = supervisor.invoke({
    "messages": [{"role": "user", "content": create}]
})

if "messages" in result:
    for msg in result["messages"]:
        role = getattr(msg, "role", type(msg).__name__)
        content = getattr(msg, "content", str(msg))
        print(f"🧠 [{role}] {content}")