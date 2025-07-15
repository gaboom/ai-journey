AI Journey
===

Run and connect to LLM
---
* [ochat/ochat.py](ochat/ochat.py): a command line python tool for streamed llm invocation, supporting image attachments

Tools/Functions facility
---
* [tool/poc.py](tool/poc.py): understand how the tool callback is working
* [tool/langchain.py](tool/langchain.py): POC tool use in LangChain
* [tool/llamaindex.py](tool/llamaindex.py): POC tool use in LlamaIndex

Model Context Protocol
---
* [mcp/server.py](mcp/server.py): POC MCP Server, HTTP Streaming example
* [mcp/client.py](mcp/client.py): POC MCP client to test the server (also verified by https://github.com/modelcontextprotocol/inspector)
* [mcp/mcp_client.py](mcp/mcp_client.py): POC using LangChain and experimental SCP server discovery [mcp/mcp_toolkit.py](mcp/mcp_toolkit.py) and universal dispatcher [mcp/mcp_tool.py](mcp/mcp_tool.py). Demonstrates realtime streaming ability.
* [mcp-profile/mcp_profile.py](mcp-profile/mcp_profile.py): A simple, stdio-based MCP server with a single tool.

Agentic MCP:
* [mcp/chat.py](mcp/chat.py)

Agentic Workflow
---
* [adk-agent/agent.py](adk-agent/agent.py): Google Agent Development Kit (ADK) based POC that orchestrates tool use and can be monitored. Supports desired tool discovery out-of-the-box!
* [adk-mcp/agent.py](adk-mcp/agent.py): An ADK agent that uses stdio-based MCP servers for local tool execution.

Future projects
===
* https://github.com/gaboom/ai-bob a planned pi based physical assistant, currently a POC for realtime bi-directional audio streaming with openai realtime api.
* https://github.com/gaboom/baios Operating system for AI agents.

Notes
===
Openai API Key, Google API Studio API Key, Python, Ollama, ADK and other tools required.
https://github.com/google-gemini/gemini-cli was extensively used.
