# AI Assistant Chat with Nmap Tool Integration

This project provides a web-based chat interface using Gradio where users can interact with an AI assistant powered by the OpenAI API. The assistant is equipped with tools to interact with the local filesystem and perform network scans using a containerized Nmap server.

## Overview

The application uses the OpenAI Agents SDK framework. User requests are processed by an AI agent that can reason about the request and decide whether to use available tools. It features:

* A Gradio frontend for easy interaction.
* An AI agent backend leveraging an OpenAI model (requires API key).
* A Model Context Protocol (MCP) server for filesystem access (using `@modelcontextprotocol/server-filesystem`).
* A containerized MCP server providing Nmap scanning capabilities (ping, port scans, service discovery, SMB share enumeration)[cite: 14, 16, 18, 20, 22].

The Nmap server runs inside a Docker container for easy dependency management and isolation.

## Features

* Conversational AI assistant.
* Filesystem access tool (scoped to the application directory).
* Network scanning tools via Nmap:
    * `ping_host` [cite: 14]
    * `scan_network` (Top 100 ports) [cite: 16]
    * `all_scan_network` (-A comprehensive scan) [cite: 18]
    * `all_ports_scan_network` (All 65535 ports) [cite: 20]
    * `smb_share_enum_scan` (SMB Share Enumeration) [cite: 22]
* Web-based UI using Gradio[cite: 11, 12].
* Containerized Nmap tool server using Docker.

## Architecture

1.  **Gradio UI (`app.txt`)**: Handles user input and displays conversation history.
2.  **Main Application (`app.txt`)**:
    * Initializes Gradio interface.
    * Manages conversation state.
    * Sets up and manages MCP servers.
    * Instantiates and runs the OpenAI Agent.
3.  **OpenAI Agent (`agents` library)**: Processes user messages, calls tools when needed, and generates responses[cite: 1, 3].
4.  **MCP Servers**:
    * **Filesystem Server**: Runs via `npx` to provide local file access[cite: 1].
    * **Nmap Toolkit Server (`nmap-server.txt` in Docker)**: Runs inside a Docker container, exposing Nmap scan functions as tools via MCP[cite: 2, 14]. `app.txt` uses `docker run` to start this server for each request.

## Prerequisites

* **Python**: 3.9+
* **Docker**: Latest version installed and running.
* **Node.js/npm**: Required for `npx` to run the filesystem MCP server.
* **OpenAI API Key**: Set as an environment variable `OPENAI_API_KEY`.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Set OpenAI API Key:**
    Export your API key as an environment variable. Replace `your_api_key_here` with your actual key.
    * Linux/macOS:
        ```bash
        export OPENAI_API_KEY='your_api_key_here'
        ```
    * Windows (Command Prompt):
        ```bash
        set OPENAI_API_KEY=your_api_key_here
        ```
    * Windows (PowerShell):
        ```bash
        $env:OPENAI_API_KEY='your_api_key_here'
        ```

3.  **Build the Nmap Docker Image:**
    Navigate to the directory containing `nmap-server.py` and `Dockerfile`, then run:
    ```bash
    docker build -t nmap-mcp-server .
    ```
    *(Ensure the `Dockerfile` content is correct, especially the MCP package name if it's not `modelcontextprotocol`)*

4.  **Install Python Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    # Activate the virtual environment
    # Linux/macOS:
    source venv/bin/activate
    # Windows:
    .\venv\Scripts\activate
    # Install requirements
    pip install -r requirements.txt
    ```

## Running the Application

Ensure your OpenAI API key is set, Docker is running, and you are in the project's root directory with the virtual environment activated.

```bash
python app.py
 An example MCP server with a couple nmap scans as tools.
