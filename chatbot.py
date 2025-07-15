
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from doctor_database import TOOLS
from patients_database import PATIENTS_TOOL

from llm_config import load_llm

class AppointBot:
    def __init__(self):
        """Initialize the chatbot with improved architecture."""
        self.llm = load_llm() #load the LLM
        self.tools = TOOLS + PATIENTS_TOOL
        self.memory = MemorySaver()
        self.graph = self._create_graph()
        
    def _create_graph(self):
        """Create the LangGraph workflow with memory management."""
        
        def agent(state: MessagesState):
            """Enhanced agent with medical appointment context."""
            messages = state["messages"]
            
            # Add medical context to system prompt
            system_prompt = self._get_medical_system_prompt()
            
            # Ensure system prompt is included
            if not messages or not self._has_system_prompt(messages):
                
                system_message = SystemMessage(content=system_prompt)
                messages = [system_message] + messages
            
            # Bind tools and get response
            model_with_tools = self.llm.bind_tools(self.tools)
            response = model_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        # Create the graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", agent)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Add edges with automatic tool detection
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            lambda x: "tools" if x["messages"][-1].tool_calls else "__end__",
            ["tools", "__end__"]
        )
        workflow.add_edge("tools", "agent")
        
        # Compile with memory persistence
        return workflow.compile(checkpointer=self.memory)
    
    def _get_medical_system_prompt(self):
        """Get comprehensive medical appointment system prompt."""
        return """You are a comprehensive medical appointment booking assistant.

                Sound polite, calm and caringing
                If the user tell about there problem or symptoms, ask more and save it as the user symptom
                After a while if the symptoms are serious or if the user wants to book an appointment with the doctor make an appointment with the specialist doctor
                If they say yes they would like to book then ask for the other details
                Only book an appointment when you have all the required details of the patient and the doctor that you recommended 
                
                CRITICAL TOOL USAGE RULES:
                - NEVER promise to do something without immediately doing it
                - When user confirms wanting to book appointment, IMMEDIATELY use get_doctors_by_specialty tool
                - Do not explain what you will do - just do it
                - Actions must be taken in the same response, not promised for later
                - Show doctors details in a tabular format
                - Ask which date does the user wants to book the appointment if there are multiple dates or time

                CORE RESPONSIBILITIES:
                - Find doctors by specialty and availability
                - Book appointments with patient information
                - Manage existing appointments (view, cancel)
                - Track patient appointment history

                AVAILABLE TOOLS:
                Doctor Management:
                - get_doctors_by_specialty: Find doctors by medical specialty
                - check_doctor_availability: Check specific doctor availability

                Patient Appointment Management:
                - book_patient_appointment: Book appointment with patient details (only execute this when you have all the details realted to patient and doctor)
                - get_patient_appointments: View patient's appointment history
                - cancel_appointment: Cancel appointments by ID

                BOOKING WORKFLOW:
                1. User mentions symptoms → Find appropriate specialty
                2. Use get_doctors_by_specialty to show available doctors
                3. When user selects doctor → Ask for patient name and age
                4. Use book_patient_appointment to complete booking
                5. Confirm appointment details

                PATIENT INFORMATION REQUIRED:
                - Patient Name (required)
                - Patient Age (required)
                - Symptoms/Reason for visit (optional but helpful)

                FORBIDDEN RESPONSES:
                ❌ "I will find doctors for you"
                ❌ "Let me search for specialists"
                ❌ "I can help you with that. First, I need to find..."

                EXAMPLE INTERACTION:
                User: "I have chest pain, can you book an appointment?"
                Assistant: [Shows available cardiologists]
                User: "Book with Dr. Smith"
                Assistant: "I'll book with Dr. Smith. Please provide patient name and age."
                User: "John Doe, 35 years old"
                Assistant: [Books appointment with patient details]
                User: "Yeah okay" (to booking question)
                Assistant: [Calls get_doctors_by_specialty) immediately and shows results]

                IMPORTANT: Always collect patient name and age before booking appointments."""
    
    def _has_system_prompt(self, messages):
        """Check if system prompt is already present."""
        if messages and hasattr(messages[0], 'content'):
            return "medical appointment booking assistant" in messages[0].content
        return False
    
    def chat(self, message: str, thread_id: str = "default"):
        """Chat with automatic memory management."""
        
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke graph with memory
        response = self.graph.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=config
        )
        
        return response["messages"][-1].content



if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    bot = AppointBot()

    result = bot.graph.invoke({"messages": [HumanMessage(content="Show me doctors that deals with Cardiology")]})
    print(result["messages"][-1].content)