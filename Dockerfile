# Dockerfile

# Use a minimal Python base image
FROM python:3.11-slim

# Install nmap and ping (required by your script)
# Using --no-install-recommends to keep the image small
RUN apt-get update && \
    apt-get install -y nmap iputils-ping --no-install-recommends && \
    # Clean up apt cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# Install required Python libraries
# Make sure 'modelcontextprotocol' is the correct package name for mcp.server.fastmcp
# Adjust if necessary based on your actual MCP library installation.
RUN pip install --no-cache-dir python-nmap modelcontextprotocol mcp

# Copy the server script into the image
COPY nmap-server.py /app/nmap-server.py

# Set the working directory
WORKDIR /app

# Command to run the MCP server when the container starts
ENTRYPOINT ["python", "nmap-server.py"]