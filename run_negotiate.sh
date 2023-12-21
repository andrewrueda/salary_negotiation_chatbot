#!/bin/bash

file_path="/.ollama/models/manifests/registry.ollama.ai/library/llama2/latest"

# Check if file exists
if [ -e "$file_path" ]; then
  echo "Found llama2 model using Ollama..."
else
  echo "llama2 not on computer. Downloading..."

  command="ollama pull llama2"
  $command

  if [ $? -eq 0 ]; then
    echo "Download successful!"
  else
    echo "Download failed. Makde sure you have Ollama installed."
    exit 1
  fi
fi