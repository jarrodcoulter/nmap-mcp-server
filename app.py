import os
import asyncio
import shlex
import shutil
import gradio as gr

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio

# Ensure required environment variables are present
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OpenAI API key. Set the OPENAI_API_KEY environment variable.")

# Check that npx is available
if not shutil.which("npx"):
    raise RuntimeError("npx is not installed or not found in PATH. Please install it (e.g., via npm).")

# Check that docker is available
if not shutil.which("docker"):
    raise RuntimeError("docker is not installed or not found in PATH. Please install Docker.")

# Setup the MCP servers for toolkit and filesystem
allowed_path = os.path.dirname(os.path.abspath(__file__))
fs_command = f"npx -y @modelcontextprotocol/server-filesystem {allowed_path}"
filesystem_server = MCPServerStdio(
    name="Filesystem MCP Server",
    params={"command": fs_command.split(" ")[0], "args": fs_command.split(" ")[1:]}
)

toolkit_cmd = "docker run --rm -i nmap-mcp-server" # Use -i for stdio, --rm to cleanup
toolkit_server = MCPServerStdio(
    name="NetworkScanner",
    params={"command": shlex.split(toolkit_cmd)[0], "args": shlex.split(toolkit_cmd)[1:]},
    cache_tools_list=True
)

AGENT_INSTRUCTIONS = (
    "You are a helpful assistant. Use available tools when needed and explain your steps."
)

def create_agent(mcp_fs, mcp_toolkit):
    return Agent(
        name="Assistant",
        instructions=AGENT_INSTRUCTIONS,
        mcp_servers=[mcp_fs, mcp_toolkit]
    )

async def process_user_message(user_message, conversation_state):
    """
    Handle a user message by running the Agent with the MCP servers.
    Returns the assistant's combined response and the updated conversation state.
    """
    if not conversation_state:
        agent_input = user_message
    else:
        agent_input = conversation_state + [{"role": "user", "content": user_message}]

    async with filesystem_server as fs, toolkit_server as toolkit:
        agent = create_agent(fs, toolkit)
        trace_id = gen_trace_id()
        with trace(workflow_name="AssistantConversation", trace_id=trace_id):
            result = await Runner.run(agent, agent_input)
    
    assistant_response_parts = []
    for item in result.new_items:
        if item.type == "reasoning_item":
            try:
                thought_text = item.raw_item.content
            except Exception:
                thought_text = str(item.raw_item)
            assistant_response_parts.append(f"**Assistant’s thoughts:** {thought_text}")
        elif item.type == "tool_call_item":
            try:
                tool_name = item.raw_item.name
            except Exception:
                tool_name = str(item.raw_item)
            try:
                tool_args = item.raw_item.arguments if hasattr(item.raw_item, "arguments") else item.raw_item.get("arguments", {})
            except Exception:
                tool_args = {}
            assistant_response_parts.append(f"**Assistant invoked tool `{tool_name}`** with arguments: `{tool_args}`")
        elif item.type == "tool_call_output_item":
            tool_output = item.output
            assistant_response_parts.append(f"**Tool output:** `{tool_output}`")
        elif item.type == "message_output_item":
            try:
                message_text = item.raw_item.content
            except Exception:
                message_text = str(item.raw_item)
            assistant_response_parts.append(f"**Assistant:** {message_text}")

    final_answer = result.final_output
    if isinstance(final_answer, str):
        if not any(final_answer in part for part in assistant_response_parts):
            assistant_response_parts.append(f"**Assistant:** {final_answer}")
    else:
        assistant_response_parts.append(f"**Assistant:** {str(final_answer)}")

    assistant_message = "\n\n".join(assistant_response_parts)
    new_conversation_state = result.to_input_list()

    return assistant_message, new_conversation_state

# Define the Gradio interface with custom CSS for scaling
css = """
html, body, .gradio-container {
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
}
.gr-chatbot {
    height: calc(100vh - 180px) !important;
}
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("## 🤖 AI Assistant Chat (Gradio Edition)\nThis chat interface uses Gradio and the OpenAI Agents SDK with MCP tools.")
    chatbot = gr.Chatbot(label="AI Assistant")
    user_input = gr.Textbox(placeholder="Type your question here...", label="Your Message")
    clear_btn = gr.Button("Clear Conversation")
    conversation_state = gr.State([])

    async def respond(message, chat_history, conv_state):
        chat_history = chat_history or []
        chat_history.append((f"**User:** {message}", ""))
        assistant_message, new_state = await process_user_message(message, conv_state)
        chat_history[-1] = (f"**User:** {message}", assistant_message)
        # Return updated chat history, conversation state, and clear the input textbox.
        return chat_history, new_state, ""

    user_input.submit(respond, [user_input, chatbot, conversation_state], [chatbot, conversation_state, user_input])
    clear_btn.click(lambda: ([], [], ""), outputs=[chatbot, conversation_state, user_input])

if __name__ == "__main__":
    demo.launch()
