AI Journey
===

Run and connect to LLM
---
* ochat/ochat.py: a command line python tool for streamed llm invocation, supporting image attachments

Tools/Functions facility
---
* tool/poc.py: understand how the tool callback is working
* tool/langchain.py: poc tool use in LangChain
* tool/llamaindex.py: poc tool use in LlamaIndex

Model Context Protocol
---
* mcp/server.py: POC MCP Server, HTTP Streaming example
* mcp/client.py: POC MCP client to test the server (also verified by https://github.com/modelcontextprotocol/inspector)
* mcp/mcp_client.py: POC using LangChain and experimental SCP server discovery mcp/mcp_toolkit.py and universal dispatcher mcp/mcp_tool.py. Demonstrates realtime streaming ability.

Agentic Workflow
---
* adk_agent/agent.py Google Agent Development Kit (ADK) based POC, the orchestrates tool use and can be monitored. Platform supports SCP server function discovery out-of-the-box! 

Future projects
===
* https://github.com/gaboom/ai-bob a planned pi based physical assistant, currently a POC for realtime bi-directional audio streaming with openai realtime api.
* https://github.com/gaboom/baios Operating system for AI agents.

Notes
===
Openai API Key, Google API Studio API Key, Python, Ollama, ADK and other tools required.
https://github.com/google-gemini/gemini-cli was extensively used.
