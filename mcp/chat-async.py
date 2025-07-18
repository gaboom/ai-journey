
"""
A command-line tool to interact with OpenAI models using the new responses API,
including support for remote tools like MCP.

Usage:
    python mcp/chat-async.py

Requirements:
    - openai: The official OpenAI Python library.
    - OPENAI_API_KEY: An environment variable containing your OpenAI API key.
"""
import asyncio
import base64
import json
import os
import sys
import traceback
from typing import Any, Dict, List, Optional, Union

from mcp import types
import openai
from openai import AsyncOpenAI, AsyncStream
from openai.types.responses import ResponseInputParam, ResponseInputItemParam, ResponseStreamEvent, WebSearchToolParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from openai.types.responses.response_input_param import FunctionCallOutput
from openai.types.responses.tool_param import ToolParam, ImageGeneration
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from openai.types.responses.response_function_call_arguments_delta_event import ResponseFunctionCallArgumentsDeltaEvent
from openai.types.responses.response_function_call_arguments_done_event import ResponseFunctionCallArgumentsDoneEvent
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from openai.types.responses.response_image_gen_call_completed_event import ResponseImageGenCallCompletedEvent
from openai.types.responses.response_queued_event import ResponseQueuedEvent
from openai.types.responses.response_in_progress_event import ResponseInProgressEvent
from openai.types.responses.response_failed_event import ResponseFailedEvent
from openai.types.responses.response_completed_event import ResponseCompletedEvent
from openai.types.responses.response_web_search_call_in_progress_event import ResponseWebSearchCallInProgressEvent
from openai.types.responses.response_web_search_call_completed_event import ResponseWebSearchCallCompletedEvent
from openai.types.responses.response_web_search_call_searching_event import ResponseWebSearchCallSearchingEvent
from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from openai.types.responses.response_content_part_added_event import ResponseContentPartAddedEvent
from openai.types.responses.response_text_done_event import ResponseTextDoneEvent
from openai.types.responses.response_content_part_done_event import ResponseContentPartDoneEvent
from openai.types.responses.response_output_item_done_event import ResponseOutputItemDoneEvent
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.types.responses.response_file_search_tool_call import ResponseFileSearchToolCall
from openai.types.responses.response_function_web_search import ResponseFunctionWebSearch, ActionSearch, ActionOpenPage, ActionFind
from openai.types.responses.response_computer_tool_call import ResponseComputerToolCall
from openai.types.responses.response_reasoning_item import ResponseReasoningItem
from openai.types.responses.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
from openai.types.responses.response_output_item import (
    ImageGenerationCall,
    LocalShellCall,
    McpCall,
    McpListTools,
    McpApprovalRequest,
)
from openai.types.responses.response_audio_delta_event import ResponseAudioDeltaEvent
from openai.types.responses.response_audio_done_event import ResponseAudioDoneEvent
from openai.types.responses.response_audio_transcript_delta_event import ResponseAudioTranscriptDeltaEvent
from openai.types.responses.response_audio_transcript_done_event import ResponseAudioTranscriptDoneEvent
from openai.types.responses.response_code_interpreter_call_code_delta_event import ResponseCodeInterpreterCallCodeDeltaEvent
from openai.types.responses.response_code_interpreter_call_code_done_event import ResponseCodeInterpreterCallCodeDoneEvent
from openai.types.responses.response_code_interpreter_call_completed_event import ResponseCodeInterpreterCallCompletedEvent
from openai.types.responses.response_code_interpreter_call_in_progress_event import ResponseCodeInterpreterCallInProgressEvent
from openai.types.responses.response_code_interpreter_call_interpreting_event import ResponseCodeInterpreterCallInterpretingEvent
from openai.types.responses.response_error_event import ResponseErrorEvent
from openai.types.responses.response_incomplete_event import ResponseIncompleteEvent
from openai.types.responses.response_refusal_delta_event import ResponseRefusalDeltaEvent
from openai.types.responses.response_refusal_done_event import ResponseRefusalDoneEvent
from openai.types.responses.response_reasoning_delta_event import ResponseReasoningDeltaEvent
from openai.types.responses.response_reasoning_done_event import ResponseReasoningDoneEvent
from openai.types.responses.response_reasoning_summary_delta_event import ResponseReasoningSummaryDeltaEvent
from openai.types.responses.response_reasoning_summary_done_event import ResponseReasoningSummaryDoneEvent
from openai.types.responses.response_reasoning_summary_part_added_event import ResponseReasoningSummaryPartAddedEvent
from openai.types.responses.response_reasoning_summary_part_done_event import ResponseReasoningSummaryPartDoneEvent
from openai.types.responses.response_reasoning_summary_text_delta_event import ResponseReasoningSummaryTextDeltaEvent
from openai.types.responses.response_reasoning_summary_text_done_event import ResponseReasoningSummaryTextDoneEvent
from openai.types.responses.response_file_search_call_completed_event import ResponseFileSearchCallCompletedEvent
from openai.types.responses.response_file_search_call_in_progress_event import ResponseFileSearchCallInProgressEvent
from openai.types.responses.response_file_search_call_searching_event import ResponseFileSearchCallSearchingEvent
from openai.types.responses.response_image_gen_call_generating_event import ResponseImageGenCallGeneratingEvent
from openai.types.responses.response_image_gen_call_in_progress_event import ResponseImageGenCallInProgressEvent
from openai.types.responses.response_image_gen_call_partial_image_event import ResponseImageGenCallPartialImageEvent
from openai.types.responses.response_mcp_call_arguments_delta_event import ResponseMcpCallArgumentsDeltaEvent
from openai.types.responses.response_mcp_call_arguments_done_event import ResponseMcpCallArgumentsDoneEvent
from openai.types.responses.response_mcp_call_completed_event import ResponseMcpCallCompletedEvent
from openai.types.responses.response_mcp_call_failed_event import ResponseMcpCallFailedEvent
from openai.types.responses.response_mcp_call_in_progress_event import ResponseMcpCallInProgressEvent
from openai.types.responses.response_mcp_list_tools_completed_event import ResponseMcpListToolsCompletedEvent
from openai.types.responses.response_mcp_list_tools_failed_event import ResponseMcpListToolsFailedEvent
from openai.types.responses.response_mcp_list_tools_in_progress_event import ResponseMcpListToolsInProgressEvent
from openai.types.responses.response_output_text_annotation_added_event import ResponseOutputTextAnnotationAddedEvent

from mcp_client_agent import ToolFunctionCall, ToolFunctionResult

class Agent: # todo debug log only
    """
    An agent that uses the OpenAI responses API to interact with the user
    and handle tool calls.
    """
    
    type ResponseInput = str | ResponseInputParam | ResponseInputItemParam

    def __init__(self) -> None:
        # --- Configuration ---
        self.MODEL: str = "gpt-4.1" 
        self.INSTRUCTIONS: str = "You are an agent of delight. Use the tools provided."
        self.TOOLS: List[ToolParam] = []
        self.FUNCTIONS: dict[str, ToolFunctionCall] = {}

        # --- Tool Definitions ---
        
        # Conversation ending function :)
        TERMINATOR_FUNCTION_NAME: str = "bye"
        TERMINATOR_TOOLS: List[FunctionToolParam] = [{
            "type": "function",
            "name": TERMINATOR_FUNCTION_NAME,
            "description": "Call this function to end the conversation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True,
        }]
        self.TOOLS.extend(TERMINATOR_TOOLS)
        self.FUNCTIONS[TERMINATOR_FUNCTION_NAME] = self.terminate

        web_search = WebSearchToolParam(
            type="web_search_preview",
        )
        self.TOOLS.append(web_search)

        image_generation = ImageGeneration(
            type="image_generation",
            output_format="png",
        )
        self.TOOLS.append(image_generation)

        # --- Event Handler Lookup Dict ---
        # self._event_handlers = { ... }  # Remove this dictionary entirely

        # --- State ---
        self.RUNNING: bool = False
        self.client: AsyncOpenAI = self._initialize_client()
        self.last_response_id: Optional[str] = None
        self.sequence_number: int = 0

    def _initialize_client(self) -> AsyncOpenAI: # TODO raise Exception instead of sys.exit and logging
        """Checks for API key and initializes the OpenAI client."""
        if not os.environ.get("OPENAI_API_KEY"):
            sys.stderr.write("Error: OPENAI_API_KEY environment variable not set.\n")
            sys.exit(1)
        try:
            return AsyncOpenAI()
        except Exception as e:
            sys.stderr.write(f"Error initializing OpenAI client: {e}\n")
            sys.exit(1)

    async def _create_response(self, input: ResponseInput) -> AsyncStream[ResponseStreamEvent]:
        """Utility method to create a response from the OpenAI client given user input."""
        if not isinstance(input, list) and not isinstance(input, str):
            input = [input]
        # TODO: should this really not return without await?
        return await self.client.responses.create( # TODO more parametrization
            background=True,
            stream=True,
            store=True,
            model=self.MODEL,
            tools=self.TOOLS,
            input=input,
            instructions=self.INSTRUCTIONS,
            previous_response_id=self.last_response_id,
        )

    def _handle_function_result(self, functionCall: ResponseFunctionToolCall, result: ToolFunctionResult) -> FunctionCallOutput:
        """Handles a function result from the model's response."""
        return FunctionCallOutput(
            type="function_call_output",
            call_id=functionCall.call_id,
            output=str(result)
        )

    def _handle_function_call(self, functionCall: ResponseFunctionToolCall) -> FunctionCallOutput:
        """Handles a function call from the model's response."""
        function: ToolFunctionCall = self.FUNCTIONS[functionCall.name]
        result = function(json.loads(functionCall.arguments))
        print(f"[system] function='{functionCall}' result='{result}'", flush=True)
        return self._handle_function_result(functionCall, result)

    def _handle_image_generation(self, id:str, image: str) -> None:
        print(f"[system] image='{id}.png'", flush=True)
        with open(f"{id}.png", "wb") as f:
            f.write(base64.b64decode(image))
    
    # Validated handlers in order

    def _on_response_created(self, event: ResponseCreatedEvent):
        """Response object created, queued for processing."""
        self.last_response_id = event.response.id
        pass

    def _on_response_queued(self, event: ResponseQueuedEvent):
        """Response has been queued but not yet started."""
        self.last_response_id = event.response.id
        pass

    def _on_response_in_progress(self, event: ResponseInProgressEvent):
        """Response is currently being processed."""
        self.last_response_id = event.response.id
        pass

    def _on_response_output_item_added(self, event: ResponseOutputItemAddedEvent):
        """An output item (such as a message, function call, or other result) was added to the response."""
        pass # part start: event.item.id, event.item.status=in progress

    # opt event.item.type=message: event.item.content=[]
     
    def _on_response_content_part_added(self, event: ResponseContentPartAddedEvent):
        """A content part (text, refusal, etc.) was added to an output item."""
        pass # part generating: event.item_id, event.part.type = output_text

    def _on_response_output_text_delta(self, event: ResponseTextDeltaEvent):
        """Streaming text output (token/partial text) from the model."""
        print(event.delta, end="", flush=True)
        pass # part receiving delta: event.item_id 

    def _on_response_output_text_done(self, event: ResponseTextDoneEvent):
        """Streaming text output is finalized for a content part."""
        pass # part done: event.item_id, event.text

    def _on_response_content_part_done(self, event: ResponseContentPartDoneEvent):
        """A content part (text, refusal, etc.) is finalized for an output item."""
        pass # part done: event.item_id, event.part.type = output_text, event.part.text

    # alt event.item.type=function_call: event.item.arguments='', event.item.call_id

    def _on_response_function_call_arguments_delta(self, event: ResponseFunctionCallArgumentsDeltaEvent):
        """Streaming function call arguments (partial arguments for a function/tool call)."""
        pass # event.item_id

    def _on_response_function_call_arguments_done(self, event: ResponseFunctionCallArgumentsDoneEvent):
        """Function call arguments complete; all arguments for the function/tool call have been streamed."""
        pass # function call arguments done: event.item_id, event.arguments

    # opt end
    
    def _on_response_output_item_done(self, event: ResponseOutputItemDoneEvent):
        """An output item (message, function call, etc.) is finalized."""
        item = event.item
        if isinstance(item, ResponseOutputMessage):
            pass # for message in item.content
        elif isinstance(item, ResponseFileSearchToolCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, ResponseFunctionToolCall):
            print(f"[system] function_call='{item.call_id}' arguments='{item.arguments}'", flush=True)
            itemResult = self._handle_function_call(item)
            
            # functionStream is an AsyncStream, not a coroutine; we should iterate it asynchronously.
            # Since we're in a sync context, use asyncio.run with an async helper.
            async def handle_events(itemResult):
                stream = await self._create_response(itemResult)  # todo async ?
                async for event in stream:
                    print(f"[system] functionEvent='{event}'", flush=True)
                    #self._handle_event(event)
            asyncio.create_task(handle_events(itemResult))
        elif isinstance(item, ResponseFunctionWebSearch):
            action = item.action
            if isinstance(action, ActionSearch):
                print(f"[web_search] Searching for: '{action.query}'", flush=True)
            elif isinstance(action, ActionOpenPage):
                print(f"[web_search] Opened page: {action.url}", flush=True)
            elif isinstance(action, ActionFind):
                print(f"[web_search] Searched for pattern '{action.pattern}' in page: {action.url}", flush=True)
            else:
                raise ValueError(f"Unexpected response item action for {item.type}: {action}")
        elif isinstance(item, ResponseComputerToolCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, ResponseReasoningItem):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, ResponseCodeInterpreterToolCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, ImageGenerationCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, LocalShellCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, McpCall):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, McpListTools):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        elif isinstance(item, McpApprovalRequest):
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        else:
            raise ValueError(f"Unexpected response item {item.type}: {item}")
        pass # response in full: event.item.id, response.item.status = completed, _ in event.item.content IF event.item.type=message; event.item.call_id, event.item.arguments IF event.item.type=function_call
    
    def _on_response_completed(self, event: ResponseCompletedEvent):
        """The response has finished processing."""
        self.last_response_id = event.response.id
        pass

    def _on_response_failed(self, event: ResponseFailedEvent):
        """The response failed due to an error."""
        pass # response failed

    # End of solid handlers

    def _on_response_image_generation_call_completed(self, event: ResponseImageGenCallCompletedEvent):
        """Image generation tool call completed; result (image) is available."""
        pass

    def _on_response_web_search_call_in_progress(self, event: ResponseWebSearchCallInProgressEvent):
        """Web search tool call is in progress."""
        pass

    def _on_response_web_search_call_completed(self, event: ResponseWebSearchCallCompletedEvent):
        """Web search tool call completed; result is available."""
        pass

    def _on_response_web_search_call_searching(self, event: ResponseWebSearchCallSearchingEvent):
        """Web search tool is searching for results."""
        pass

    # Default handlers for all other event types
    def _on_response_audio_delta(self, event: ResponseAudioDeltaEvent):
        """Audio delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_audio_done(self, event: ResponseAudioDoneEvent):
        """Audio done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_audio_transcript_delta(self, event: ResponseAudioTranscriptDeltaEvent):
        """Audio transcript delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_audio_transcript_done(self, event: ResponseAudioTranscriptDoneEvent):
        """Audio transcript done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_code_interpreter_call_code_delta(self, event: ResponseCodeInterpreterCallCodeDeltaEvent):
        """Code interpreter call code delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_code_interpreter_call_code_done(self, event: ResponseCodeInterpreterCallCodeDoneEvent):
        """Code interpreter call code done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_code_interpreter_call_completed(self, event: ResponseCodeInterpreterCallCompletedEvent):
        """Code interpreter call completed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_code_interpreter_call_in_progress(self, event: ResponseCodeInterpreterCallInProgressEvent):
        """Code interpreter call in progress event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_code_interpreter_call_interpreting(self, event: ResponseCodeInterpreterCallInterpretingEvent):
        """Code interpreter call interpreting event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_error(self, event: ResponseErrorEvent):
        """Response error event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_incomplete(self, event: ResponseIncompleteEvent):
        """Response incomplete event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_refusal_delta(self, event: ResponseRefusalDeltaEvent):
        """Response refusal delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_refusal_done(self, event: ResponseRefusalDoneEvent):
        """Response refusal done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_delta(self, event: ResponseReasoningDeltaEvent):
        """Response reasoning delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_done(self, event: ResponseReasoningDoneEvent):
        """Response reasoning done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_delta(self, event: ResponseReasoningSummaryDeltaEvent):
        """Response reasoning summary delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_done(self, event: ResponseReasoningSummaryDoneEvent):
        """Response reasoning summary done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_part_added(self, event: ResponseReasoningSummaryPartAddedEvent):
        """Response reasoning summary part added event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_part_done(self, event: ResponseReasoningSummaryPartDoneEvent):
        """Response reasoning summary part done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_text_delta(self, event: ResponseReasoningSummaryTextDeltaEvent):
        """Response reasoning summary text delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_reasoning_summary_text_done(self, event: ResponseReasoningSummaryTextDoneEvent):
        """Response reasoning summary text done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_file_search_call_completed(self, event: ResponseFileSearchCallCompletedEvent):
        """File search call completed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_file_search_call_in_progress(self, event: ResponseFileSearchCallInProgressEvent):
        """File search call in progress event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_file_search_call_searching(self, event: ResponseFileSearchCallSearchingEvent):
        """File search call searching event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_image_gen_call_generating(self, event: ResponseImageGenCallGeneratingEvent):
        """Image generation call generating event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_image_gen_call_partial_image(self, event: ResponseImageGenCallPartialImageEvent):
        """Image generation call partial image event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_image_gen_call_in_progress(self, event: ResponseImageGenCallInProgressEvent):
        """Image generation call in progress event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_call_arguments_delta(self, event: ResponseMcpCallArgumentsDeltaEvent):
        """MCP call arguments delta event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_call_arguments_done(self, event: ResponseMcpCallArgumentsDoneEvent):
        """MCP call arguments done event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_call_completed(self, event: ResponseMcpCallCompletedEvent):
        """MCP call completed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_call_failed(self, event: ResponseMcpCallFailedEvent):
        """MCP call failed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_call_in_progress(self, event: ResponseMcpCallInProgressEvent):
        """MCP call in progress event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_list_tools_completed(self, event: ResponseMcpListToolsCompletedEvent):
        """MCP list tools completed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_list_tools_failed(self, event: ResponseMcpListToolsFailedEvent):
        """MCP list tools failed event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_mcp_list_tools_in_progress(self, event: ResponseMcpListToolsInProgressEvent):
        """MCP list tools in progress event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _on_response_output_text_annotation_added(self, event: ResponseOutputTextAnnotationAddedEvent):
        """Output text annotation added event."""
        raise ValueError(f"Unexpected stream event {event.type}: {event}")

    def _handle_event(self, event: ResponseStreamEvent) -> None:
        """
        Dispatches the event to the correct handler using explicit type checks.
        Raises ValueError if the event type is not recognized.
        """
        if isinstance(event, ResponseCreatedEvent):
            self._on_response_created(event)
        elif isinstance(event, ResponseQueuedEvent):
            self._on_response_queued(event)
        elif isinstance(event, ResponseInProgressEvent):
            self._on_response_in_progress(event)
        elif isinstance(event, ResponseOutputItemAddedEvent):
            self._on_response_output_item_added(event)
        elif isinstance(event, ResponseContentPartAddedEvent):
            self._on_response_content_part_added(event)
        elif isinstance(event, ResponseTextDeltaEvent):
            self._on_response_output_text_delta(event)
        elif isinstance(event, ResponseTextDoneEvent):
            self._on_response_output_text_done(event)
        elif isinstance(event, ResponseContentPartDoneEvent):
            self._on_response_content_part_done(event)
        elif isinstance(event, ResponseFunctionCallArgumentsDeltaEvent):
            self._on_response_function_call_arguments_delta(event)
        elif isinstance(event, ResponseFunctionCallArgumentsDoneEvent):
            self._on_response_function_call_arguments_done(event)
        elif isinstance(event, ResponseOutputItemDoneEvent):
            self._on_response_output_item_done(event)
        elif isinstance(event, ResponseCompletedEvent):
            self._on_response_completed(event)
        elif isinstance(event, ResponseFailedEvent):
            self._on_response_failed(event)
        elif isinstance(event, ResponseImageGenCallCompletedEvent):
            self._on_response_image_generation_call_completed(event)
        elif isinstance(event, ResponseWebSearchCallInProgressEvent):
            self._on_response_web_search_call_in_progress(event)
        elif isinstance(event, ResponseWebSearchCallCompletedEvent):
            self._on_response_web_search_call_completed(event)
        elif isinstance(event, ResponseWebSearchCallSearchingEvent):
            self._on_response_web_search_call_searching(event)
        elif isinstance(event, ResponseAudioDeltaEvent):
            self._on_response_audio_delta(event)
        elif isinstance(event, ResponseAudioDoneEvent):
            self._on_response_audio_done(event)
        elif isinstance(event, ResponseAudioTranscriptDeltaEvent):
            self._on_response_audio_transcript_delta(event)
        elif isinstance(event, ResponseAudioTranscriptDoneEvent):
            self._on_response_audio_transcript_done(event)
        elif isinstance(event, ResponseCodeInterpreterCallCodeDeltaEvent):
            self._on_response_code_interpreter_call_code_delta(event)
        elif isinstance(event, ResponseCodeInterpreterCallCodeDoneEvent):
            self._on_response_code_interpreter_call_code_done(event)
        elif isinstance(event, ResponseCodeInterpreterCallCompletedEvent):
            self._on_response_code_interpreter_call_completed(event)
        elif isinstance(event, ResponseCodeInterpreterCallInProgressEvent):
            self._on_response_code_interpreter_call_in_progress(event)
        elif isinstance(event, ResponseCodeInterpreterCallInterpretingEvent):
            self._on_response_code_interpreter_call_interpreting(event)
        elif isinstance(event, ResponseErrorEvent):
            self._on_response_error(event)
        elif isinstance(event, ResponseIncompleteEvent):
            self._on_response_incomplete(event)
        elif isinstance(event, ResponseRefusalDeltaEvent):
            self._on_response_refusal_delta(event)
        elif isinstance(event, ResponseRefusalDoneEvent):
            self._on_response_refusal_done(event)
        elif isinstance(event, ResponseReasoningDeltaEvent):
            self._on_response_reasoning_delta(event)
        elif isinstance(event, ResponseReasoningDoneEvent):
            self._on_response_reasoning_done(event)
        elif isinstance(event, ResponseReasoningSummaryDeltaEvent):
            self._on_response_reasoning_summary_delta(event)
        elif isinstance(event, ResponseReasoningSummaryDoneEvent):
            self._on_response_reasoning_summary_done(event)
        elif isinstance(event, ResponseReasoningSummaryPartAddedEvent):
            self._on_response_reasoning_summary_part_added(event)
        elif isinstance(event, ResponseReasoningSummaryPartDoneEvent):
            self._on_response_reasoning_summary_part_done(event)
        elif isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
            self._on_response_reasoning_summary_text_delta(event)
        elif isinstance(event, ResponseReasoningSummaryTextDoneEvent):
            self._on_response_reasoning_summary_text_done(event)
        elif isinstance(event, ResponseFileSearchCallCompletedEvent):
            self._on_response_file_search_call_completed(event)
        elif isinstance(event, ResponseFileSearchCallInProgressEvent):
            self._on_response_file_search_call_in_progress(event)
        elif isinstance(event, ResponseFileSearchCallSearchingEvent):
            self._on_response_file_search_call_searching(event)
        elif isinstance(event, ResponseImageGenCallGeneratingEvent):
            self._on_response_image_gen_call_generating(event)
        elif isinstance(event, ResponseImageGenCallPartialImageEvent):
            self._on_response_image_gen_call_partial_image(event)
        elif isinstance(event, ResponseImageGenCallInProgressEvent):
            self._on_response_image_gen_call_in_progress(event)
        elif isinstance(event, ResponseMcpCallArgumentsDeltaEvent):
            self._on_response_mcp_call_arguments_delta(event)
        elif isinstance(event, ResponseMcpCallArgumentsDoneEvent):
            self._on_response_mcp_call_arguments_done(event)
        elif isinstance(event, ResponseMcpCallCompletedEvent):
            self._on_response_mcp_call_completed(event)
        elif isinstance(event, ResponseMcpCallFailedEvent):
            self._on_response_mcp_call_failed(event)
        elif isinstance(event, ResponseMcpCallInProgressEvent):
            self._on_response_mcp_call_in_progress(event)
        elif isinstance(event, ResponseMcpListToolsCompletedEvent):
            self._on_response_mcp_list_tools_completed(event)
        elif isinstance(event, ResponseMcpListToolsFailedEvent):
            self._on_response_mcp_list_tools_failed(event)
        elif isinstance(event, ResponseMcpListToolsInProgressEvent):
            self._on_response_mcp_list_tools_in_progress(event)
        elif isinstance(event, ResponseOutputTextAnnotationAddedEvent):
            self._on_response_output_text_annotation_added(event)
        else:
            raise ValueError(f"Unexpected stream event {event.type}: {event}")

    async def _execute_turn(self, user_input: ResponseInput):
        """
        Executes a single turn of the conversation, handling the API call,
        streaming the response, and processing any tool calls.
        """
        stream = await self._create_response(user_input)

        async for event in stream:
            self.sequence_number = event.sequence_number # todo checker and generic response id update
            self._handle_event(event)                
        
        print() # Add a newline after text deltas
        

    def terminate(self, *_, **__) -> ToolFunctionResult: # todo add farewell message
            self.RUNNING = False
            return ToolFunctionResult(
                content=[types.TextContent(type="text", text="Conversation shall end.")],
                structuredContent=None,
                isError=False
            )

    async def run(self) -> None:
        """Runs the main conversation loop."""
        self.RUNNING = True
        self.last_response_id = None
        print(f"[system] agent='openai@{openai.__version__}' model='{self.MODEL}' instructions='{self.INSTRUCTIONS}' tools='{self.TOOLS}'.")
        
        while self.RUNNING:
            try:
                print(f"[user] ", end="", flush=True)
                user_input = await asyncio.to_thread(sys.stdin.readline)

                # Get Response using the new API
                try:
                    await self._execute_turn(user_input.strip())

                except openai.APIError as e:
                    sys.stderr.write(f"OpenAI API Error: {e}\n")
                    sys.stderr.write(f"Traceback:\n{traceback.format_exc()}\n")
                except Exception as e:
                    sys.stderr.write(f"An unexpected error occurred: {e}\n")
                    sys.stderr.write(f"Traceback:\n{traceback.format_exc()}\n")

            except (KeyboardInterrupt, EOFError):
                self.RUNNING = False
        
        print("", flush=True)

async def main() -> None:
    """
    Main function to instantiate and run the agent.
    """
    agent = Agent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
