import asyncio
import sys
from mcp.server.fastmcp import FastMCP
import nmap

# Initialize the MCP server with a name
mcp = FastMCP("Nmap Server")

@mcp.tool()
async def ping_host(ip: str) -> str:
    """Ping a host and return the raw output."""
    # Use appropriate ping count flag based on OS (-n for Windows, -c for Unix)
    count_flag = "-n" if sys.platform.startswith("win") else "-c"
    # Start the ping subprocess asynchronously (non-blocking)
    proc = await asyncio.create_subprocess_exec(
        "ping", count_flag, "4", ip,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    # Wait for the ping process to finish and collect output
    stdout, stderr = await proc.communicate()
    # Decode bytes to string and combine stdout and stderr
    output = stdout.decode() + stderr.decode()
    return output.strip()

@mcp.tool()
async def scan_network(targets: str) -> dict:
    """Scan a network/IP range for open ports (top 100 ports). If mulitple targets are provided and they are not in CIDR format, they should be space-separated."""
    # Initialize the Nmap port scanner
    scanner = nmap.PortScanner()
    # Run the scan in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: scanner.scan(hosts=targets, arguments="-T4 --top-ports 100 --open")
    )
    return result  # The scan result is a nested dictionary with scan details

@mcp.tool()
async def all_scan_network(targets: str) -> dict:
    """Scan a network/IP range with -A flag to run all basic scripts. This is the most comprehensive scan. If mulitple targets are provided and they are not in CIDR format, they should be space-separated."""
    # Initialize the Nmap port scanner
    scanner = nmap.PortScanner()
    # Run the scan in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: scanner.scan(hosts=targets, arguments="-T4 -A --open")
    )
    return result  # The scan result is a nested dictionary with scan details

@mcp.tool()
async def all_ports_scan_network(targets: str) -> dict:
    """Scan a network/IP range for all open ports. If mulitple targets are provided and they are not in CIDR format, they should be space-separated."""
    # Initialize the Nmap port scanner
    scanner = nmap.PortScanner()
    # Run the scan in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: scanner.scan(hosts=targets, arguments="-T4 -p- --open")
    )
    return result  # The scan result is a nested dictionary with scan details

@mcp.tool()
async def smb_share_enum_scan(targets: str) -> dict:
    """Scan a network/IP range and enumerate smb shares. If mulitple targets are provided and they are not in CIDR format, they should be space-separated."""
    # Initialize the Nmap port scanner
    scanner = nmap.PortScanner()
    # Run the scan in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: scanner.scan(hosts=targets, arguments="--script smb-enum-shares -p 445")
    )
    return result  # The scan result is a nested dictionary with scan details

if __name__ == "__main__":
    # Run the MCP server over stdio (for use with `mcp dev` or other stdio clients)
    mcp.run(transport="stdio")
