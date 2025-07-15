#!/bin/bash

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Verifying installation..."
ollama --version

echo "Pulling llama3-groq-tool-use:8b model..."
ollama pull llama3-groq-tool-use:8b

echo "Model pulled successfully! You can now run it with:"
echo "ollama run llama3-groq-tool-use:8b"
