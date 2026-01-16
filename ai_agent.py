"""
ai_agent.py: Custom AI agent for managing Proxmox via natural-language commands using OpenAI and proxmoxer.
This script uses OpenAI's ChatCompletion to interpret user commands and call Proxmoxer functions to manage VMs.
"""

import os
import json
from proxmoxer import ProxmoxAPI
import openai

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
PROXMOX_TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_VERIFY_SSL = os.getenv("PROXMOX_VERIFY_SSL", "True") == "True"

# Initialize Proxmox connection using token
proxmox = ProxmoxAPI(
    PROXMOX_HOST,
    user=PROXMOX_USER,
    token_name=PROXMOX_TOKEN_ID,
    token_value=PROXMOX_TOKEN_SECRET,
    verify_ssl=PROXMOX_VERIFY_SSL,
)

# Set up OpenAI client
openai.api_key = OPENAI_API_KEY

# Example function to create VM
def create_vm(node, vmid, name, memory=2048, cores=2, disk='32G', iso_storage='local', iso_file=''):
    """Create a new VM on given node with specified resources."""
    return proxmox.nodes(node).qemu.create(
        vmid=vmid,
        name=name,
        memory=memory,
        cores=cores,
        scsihw='virtio-scsi-pci',
        sata0=f"{iso_storage}:{disk}",
        ide2=f"{iso_storage}:iso/{iso_file},media=cdrom",
        net0='virtio,bridge=vmbr0'
    )

# Example function to start VM
def start_vm(node, vmid):
    return proxmox.nodes(node).qemu(vmid).status.start.post()

# Example function to stop VM
def stop_vm(node, vmid):
    return proxmox.nodes(node).qemu(vmid).status.stop.post()

# Example function to list VMs
def list_vms(node):
    return proxmox.nodes(node).qemu.get()

# Define available functions for AI to call
AVAILABLE_FUNCTIONS = {
    "create_vm": create_vm,
    "start_vm": start_vm,
    "stop_vm": stop_vm,
    "list_vms": list_vms,
}

# Chat function definitions for OpenAI function calling
FUNCTION_DEFS = [
    {
        "name": "create_vm",
        "description": "Create a new virtual machine on a Proxmox node.",
        "parameters": {
            "type": "object",
            "properties": {
                "node": {"type": "string", "description": "Proxmox node name"},
                "vmid": {"type": "integer", "description": "Unique ID for the VM"},
                "name": {"type": "string", "description": "Name of the new VM"},
                "memory": {"type": "integer", "description": "RAM in megabytes"},
                "cores": {"type": "integer", "description": "Number of CPU cores"},
                "disk": {"type": "string", "description": "Disk size (e.g. '32G')"},
                "iso_storage": {"type": "string", "description": "Storage location for ISO"},
                "iso_file": {"type": "string", "description": "ISO filename"},
            },
            "required": ["node", "vmid", "name"],
        },
    },
    {
        "name": "start_vm",
        "description": "Start a virtual machine.",
        "parameters": {
            "type": "object",
            "properties": {
                "node": {"type": "string", "description": "Proxmox node name"},
                "vmid": {"type": "integer", "description": "ID of the VM"},
            },
            "required": ["node", "vmid"],
        },
    },
    {
        "name": "stop_vm",
        "description": "Stop a virtual machine.",
        "parameters": {
            "type": "object",
            "properties": {
                "node": {"type": "string"},
                "vmid": {"type": "integer"},
            },
            "required": ["node", "vmid"],
        },
    },
    {
        "name": "list_vms",
        "description": "List all VMs on a node.",
        "parameters": {
            "type": "object",
            "properties": {"node": {"type": "string"}},
            "required": ["node"],
        },
    },
]

def run_agent(system_prompt: str = "You are a Proxmox assistant."):
    """Run an interactive loop reading user input and performing tasks via Proxmox."""
    messages = [{"role": "system", "content": system_prompt}]
    while True:
        user_input = input("User: ")
        messages.append({"role": "user", "content": user_input})
        # Call OpenAI with function calling
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=messages,
            functions=FUNCTION_DEFS,
            function_call="auto",
        )
        reply = response["choices"][0]["message"]
        if reply.get("function_call"):
            func_name = reply["function_call"]["name"]
            arguments = json.loads(reply["function_call"]["arguments"])
            result = AVAILABLE_FUNCTIONS[func_name](**arguments)
            # Add the function response to messages
            messages.append({
                "role": "function",
                "name": func_name,
                "content": str(result),
            })
            print(f"{func_name} executed: {result}")
        else:
            assistant_reply = reply["content"]
            messages.append({"role": "assistant", "content": assistant_reply})
            print(f"Assistant: {assistant_reply}")
