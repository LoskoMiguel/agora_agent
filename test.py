from langgraph_swarm import create_swarm, create_handoff_tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage

@tool
def transfer_to_hotel_agent(hotel_name: str):
    """Transferir el control al agente de hotel junto con el nombre del hotel"""
    return {
        "__handoff__": {
            "to": "hotel_agent",
            "update": {
                "hotel_name": hotel_name
            }
        }
    }

@tool
def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

@tool
def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

# Agente de vuelos
flight_agent = create_react_agent(
    name="flight_agent",
    model="gpt-4.1",
    tools=[book_flight, transfer_to_hotel_agent],
    prompt="""
    Eres un asistente de vuelos. 
    Debes realizar SOLO UNA llamada a herramienta a la vez. 
    Nunca invoques más de una herramienta en el mismo turno. 
    Si detectas que hay que reservar un hotel, primero termina la reserva de vuelo, 
    y luego haz el handoff con `transfer_to_hotel_agent`.
    """
)

# Agente de hotel
hotel_agent = create_react_agent(
    name="hotel_agent",
    model="gpt-4.1",
    tools=[book_hotel],
    prompt="Eres un asistente de hoteles"
)

# Swarm
swarm = create_swarm(
    agents=[flight_agent, hotel_agent],
    default_active_agent="flight_agent"
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

for chunk in swarm.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at Moon Hotel"
            }
        ]
    }
):
    pretty_print(chunk)