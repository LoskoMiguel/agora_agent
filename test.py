from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
import json
import os
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver() 

thread_config = {"configurable": {"thread_id": "reserva-thread"}}

def cargar_reservas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_reservas(reservas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=2, ensure_ascii=False)

DATA_FILE = "reservas.json"

# ----------------------------
# Herramientas de reserva
# ----------------------------

def add_reservation(nombre: str, fecha: str):
    """Agrega una reserva con el nombre de la persona y la fecha proporcionada."""
    reservas = cargar_reservas()
    reservas.append({"nombre": nombre, "fecha": fecha})
    guardar_reservas(reservas)
    return f"✅ Reserva agregada para {nombre} el {fecha}."

def edit_reservation(nombre: str, nueva_fecha: str):
    """Edita una reserva existente, cambiando la fecha de la reserva para el nombre dado."""
    reservas = cargar_reservas()
    for r in reservas:
        if r["nombre"].lower() == nombre.lower():
            r["fecha"] = nueva_fecha
            guardar_reservas(reservas)
            return f"✏️ Reserva para {nombre} actualizada a {nueva_fecha}."
    return f"❌ No se encontró una reserva a nombre de {nombre}."

def delete_reservation(nombre: str):
    """Elimina una reserva existente por nombre."""
    reservas = cargar_reservas()
    nuevas = [r for r in reservas if r["nombre"].lower() != nombre.lower()]
    if len(nuevas) == len(reservas):
        return f"❌ No se encontró ninguna reserva para {nombre}."
    guardar_reservas(nuevas)
    return f"🗑️ Reserva para {nombre} eliminada."


# ----------------------------
# Agentes individuales
# ----------------------------

add_agent = create_react_agent(
    name="add_agent",
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "Eres un asistente que maneja solicitudes para AGREGAR reservas. "
        "Cuando tengas toda la información, llama a la herramienta 'add_reservation' directamente con el texto que te proporcionó el usuario."
    ),
    tools=[add_reservation],
)

edit_agent = create_react_agent(
    name="edit_agent",
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "Eres un asistente que maneja solicitudes para EDITAR reservas. "
        "Cuando tengas los datos necesarios, llama a la herramienta 'edit_reservation' directamente con el texto del usuario."
    ),
    tools=[edit_reservation],
)

delete_agent = create_react_agent(
    name="delete_agent",
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "Eres un asistente que maneja solicitudes para ELIMINAR reservas. "
        "Cuando tengas los datos necesarios, llama a la herramienta 'delete_reservation' directamente con el texto del usuario."
    ),
    tools=[delete_reservation],
)

# ----------------------------
# Supervisor
# ----------------------------

supervisor = create_supervisor(
    agents=[add_agent, edit_agent, delete_agent],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "Eres el supervisor de un sistema de reservas. "
        "Tienes tres asistentes: uno para agregar, uno para editar y otro para eliminar reservas. "
        "Tu trabajo es decidir a cuál de ellos asignarle la solicitud del usuario. "
        "Pásales la solicitud tal cual para que la procesen usando sus herramientas."
    )
).compile(checkpointer=memory)

# ----------------------------
# Interacción
# ----------------------------

print("\n🎯 Sistema de reservas listo. Escribe tu solicitud:\n")

while True:
    user_input = input("Tú: ")
    if user_input.lower() in ["salir", "exit"]:
        break

    result = supervisor.invoke({
        "messages": [{"role": "user", "content": user_input}]
    },
    
    config=thread_config)

    if "messages" in result:
        for msg in result["messages"]:
            role = getattr(msg, "role", type(msg).__name__)
            content = getattr(msg, "content", str(msg))
            print(f"🧠 [{role}] {content}")