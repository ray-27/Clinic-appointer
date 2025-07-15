# Doctor Appointment Chatbot
A conversational AI-powered doctor appointment booking system built with Flask, LangGraph, and modern web technologies.

## Quick Start
Prerequisites
Python 3.9+
Node.js (for frontend dependencies)
Ollama or Google AI API key

## Installation
1. Clone the repository
```bash
git clone https://github.com/ray-27/Clinic-appointer.git
cd Clinic-appointer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file in the folder root directory and add these variables
```bash
LLM_SERVICE=ollama
LLM_MODEL=llama3-groq-tool-use:8b

GOOGLE_API_KEY=
```

3.1 If you want to use local LLM like Ollama you can download it using `ollama_setup.sh`, this is for UNIX based systems
```bash
sh ollama_setup.sh
```

4. Run the application
```bash
# Development
python app.py

# Production
gunicorn --bind 0.0.0.0:8080 app:app
```

5. Access the application
after the server started running, go to browser and type
```text
http://localhost:8080
```

The service is now running.

If you want to see the appointments details of all the patients that have registerd the go to 
```text
http://localhost:8080/appointments
```

## What model to choose

1. If you are using Ollama
Choose an instruct model as that will be able to execute the commands 
in the `.env` file put 
```bash
LLM_SERVICE=ollama
LLM_MODEL=llama3-groq-tool-use:8b
```
or use any other instruct model you wish

2. If you are using Gemini
Choose `Gemini-2.0-Flash`,`Gemini-2.5-Flash` or there lite version 
you can get the model detials from [Ai Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.0-flash)

modify the `.env` as 
```bash 
LLM_SERVICE=gemini
LLM_MODEL=gemini-2.0-flash
```
