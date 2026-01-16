# proxmox-ai-agent  
AI-powered assistant for managing Proxmox Virtual Environment using natural-language commands.  

## Overview  
This repository contains an AI agent that interacts with the Proxmox VE REST API to perform tasks like creating VMs, obtaining SSH access and applying configuration changes. The agent uses a language model to parse user requests and maps them to API calls via the `proxmoxer` Python library. Optionally, workflows can be orchestrated with n8n for conversational interactions.  

## Files  
- `agents.md` – describes the agent architecture, capabilities and setup.  
- `diagram.md` – contains a Mermaid diagram illustrating the system architecture.  

## Getting Started  
1. Generate an API token in Proxmox (Datacenter → Permissions → API Tokens).  
2. Install dependencies (Python 3, proxmoxer, etc.).  
3. Configure environment variables with your Proxmox host, API token and node name.  
4. Run the agent and interact via CLI or integrate with n8n for natural-language commands.  

## Architecture  
A high-level architecture diagram is provided in `diagram.md` using Mermaid syntax. The agent receives natural-language commands, interprets them with a language model, and calls the Proxmox API to perform tasks like VM creation, SSH access and configuration.
