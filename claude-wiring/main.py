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

            # Step 6: Define the user's message to Claude
            user_message = f"""
            Please do all of the following:
            1. Get the current stock price for AAPL
            2. Get the company overview for AAPL
            4. Get my bank account balances using access token {access_token}
            5. Get my recent transactions using access token {access_token}
            Then summarize everything as a financial snapshot.
            """

            system_prompt = """You are a personal AI financial advisor designed to help people of all financial backgrounds — from beginners to experienced investors. 

            You have access to real-time stock data, company fundamentals, Reddit market sentiment, and the user's personal bank data. Use these tools proactively to give personalized, actionable financial insights.

            Keep your tone friendly, clear, and jargon-free. When you use financial terms, briefly explain them. Never make the user feel judged about their financial situation. Your goal is to help them understand their money better and make informed decisions."""
            messages = [{"role": "user", "content": user_message}]

            # Step 7: Send the message to Claude, along with the tool list
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                tools=claude_tools,
                messages=messages,
            )

            print(f"\n🤖 Claude's initial response type: {response.stop_reason}")

            # Step 8: Handle tool calls in a loop
            while response.stop_reason == "tool_use":
                # Append Claude's full response to history
                messages.append({"role": "assistant", "content": response.content})

                # Collect ALL tool_use blocks in this response
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"\n🔧 Claude wants to call tool: '{tool_name}' with input: {tool_input}")

                        # Call the tool
                        tool_result = await session.call_tool(tool_name, tool_input)
                        tool_output = tool_result.content[0].text

                        print(f"📊 Tool returned: {tool_output}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_output,
                        })

                # Send all tool results back in one message
                messages.append({"role": "user", "content": tool_results})

                # Ask Claude to continue
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    tools=claude_tools,
                    messages=messages,
                )

            # Step 12: Print Claude's final answer
            final_text = next(
                block.text for block in response.content
                if hasattr(block, "text")
            )
            print(f"\n💬 Claude's final answer:\n{final_text}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(run())