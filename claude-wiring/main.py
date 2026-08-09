import asyncio
import anthropic
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from tools.bank_data import get_sandbox_access_token

load_dotenv()
access_token = get_sandbox_access_token()

# --- CONFIGURATION ---
# This tells your script where Person 1's MCP server lives.
# Update this path once you know where their server file is.
MCP_SERVER_PATH = "mock-mcp-server/server.py"
async def run():
    # Step 1: Define how to launch the MCP server
    # "stdio" means your script talks to the server through
    # standard input/output — like two programs passing notes.
    server_params = StdioServerParameters(
        command="python",
        args=[MCP_SERVER_PATH],
    )

    # Step 2: Start the MCP server and open a session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Step 3: Ask the MCP server "what tools do you have?"
            await session.initialize()
            tools_result = await session.list_tools()

            # Step 4: Convert those tools into the format Claude expects
            claude_tools = []
            for tool in tools_result.tools:
                claude_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                })

            print(f"✅ Connected to MCP server. Tools available: {[t['name'] for t in claude_tools]}")

            # Step 5: Set up the Anthropic client
            client = anthropic.Anthropic()

            system_prompt = """You are a personal AI financial advisor designed to help people of all financial backgrounds — from beginners to experienced investors. 

            You have access to real-time stock data, company fundamentals, Reddit market sentiment, and the user's personal bank data. Use these tools proactively to give personalized, actionable financial insights.

            Only answer questions related to personal finance, investing, stocks, and the user's bank data. If the user asks about anything unrelated, politely redirect them back to financial topics.

            Keep your tone friendly, clear, and jargon-free. When you use financial terms, briefly explain them. Never make the user feel judged about their financial situation. Your goal is to help them understand their money better and make informed decisions."""
            # Get Plaid token once upfront
            access_token = get_sandbox_access_token()

            print("\n💬 Welcome to your AI Financial Advisor!")
            print("Type 'exit' to quit.\n")

            messages = []

            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                messages.append({"role": "user", "content": user_input})

                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2048,
                    system=system_prompt,
                    tools=claude_tools,
                    messages=messages,
                )

                # Handle tool calls
                while response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_input = block.input

                            # Auto-inject access token for bank tools
                            if block.name in ["balances", "transactions"]:
                                tool_input = {"access_token": access_token}

                            print(f"🔧 Calling {block.name}...")
                            tool_result = await session.call_tool(block.name, tool_input)
                            tool_output = tool_result.content[0].text

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": tool_output,
                            })

                    messages.append({"role": "user", "content": tool_results})

                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=2048,
                        system=system_prompt,
                        tools=claude_tools,
                        messages=messages,
                    )

                # Get final text response
                final_text = next(
                    block.text for block in response.content
                    if hasattr(block, "text")
                )
                print(f"\n🤖 Advisor: {final_text}\n")
                messages.append({"role": "assistant", "content": response.content})

# Run the async function
if __name__ == "__main__":
    asyncio.run(run())