import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from tools.bank_data import get_sandbox_access_token

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), '..', 'mock-mcp-server', 'server.py')

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    goal: Optional[str] = ""
    risk: Optional[str] = ""
    horizon: Optional[str] = ""
    income: Optional[str] = ""

@app.post("/chat")
async def chat(request: ChatRequest):
    server_params = StdioServerParameters(
        command="python",
        args=[MCP_SERVER_PATH],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()

            claude_tools = []
            for tool in tools_result.tools:
                claude_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                })

            client = anthropic.Anthropic()
            access_token = get_sandbox_access_token()

            system_prompt = f"""You are a personal AI financial advisor designed to help people of all financial backgrounds — from beginners to experienced investors.

You have access to real-time stock data, company fundamentals, Reddit market sentiment, and the user's personal bank data. Use these tools proactively to give personalized, actionable financial insights.

Keep your tone friendly, clear, and jargon-free. When you use financial terms, briefly explain them. Never make the user feel judged about their financial situation. Your goal is to help them understand their money better and make informed decisions.

The user's bank access token is already handled by the system — never ask the user for it. Just call the balances and transactions tools directly when you need bank data.

Only answer questions related to personal finance, investing, stocks, and the user's bank data. If the user asks about anything unrelated, politely redirect them back to financial topics.

User profile:
- Financial goal: {request.goal}
- Risk tolerance: {request.risk}
- Time horizon: {request.horizon}
- Annual income: {request.income}

Use this profile to tailor all your advice to this specific user."""

            messages = [{"role": m.role, "content": m.content} for m in request.history]
            messages.append({"role": "user", "content": request.message})

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=system_prompt,
                tools=claude_tools,
                messages=messages,
            )

            while response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_input = block.input
                        if block.name in ["balances", "transactions"]:
                            tool_input = {"access_token": access_token}

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

            final_text = next(
                block.text for block in response.content
                if hasattr(block, "text")
            )

            return {"response": final_text}