import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()  # pulls ANTHROPIC_API_KEY from your .env file

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
            user_message = "What is the current stock price of AAPL?"

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
            # Claude might call multiple tools before giving a final answer
            while response.stop_reason == "tool_use":
                # Find which tool Claude wants to call
                tool_use_block = next(
                    block for block in response.content
                    if block.type == "tool_use"
                )

                tool_name = tool_use_block.name
                tool_input = tool_use_block.input

                print(f"\n🔧 Claude wants to call tool: '{tool_name}' with input: {tool_input}")

                # Step 9: Actually call the tool on the MCP server
                tool_result = await session.call_tool(tool_name, tool_input)
                tool_output = tool_result.content[0].text

                print(f"📊 Tool returned: {tool_output}")

                # Step 10: Send the tool result back to Claude
                # Claude needs to see both what it said AND what the tool returned
                messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_block.id,
                                "content": tool_output,
                            }
                        ],
                    },
                ]

                # Step 11: Ask Claude to respond now that it has the tool data
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