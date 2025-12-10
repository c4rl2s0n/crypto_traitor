import json
import logging
from typing import List, Union

from dependency_injector.wiring import inject, Provide
from openai import OpenAI
from openai.types.responses import ResponseInputParam, EasyInputMessage, EasyInputMessageParam
from openai.types.responses.response_input_param import FunctionCallOutput

from traitor.core.tools.ai.llm_agent import LLMAgent
from traitor.core.tools.ai.llm_tools import LLMTool


class LLMOpenAI(LLMAgent):
    name = "OpenAI"

    @inject
    def __init__(self, model: str = "gpt-5-nano", api_key: str = Provide["config.api_keys.OPENAI"]):
        self.model_name = model
        self.client = OpenAI(api_key=api_key)

    def process_text(self, contents: List[str]) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            input=self._prepare_contents(contents),
            service_tier="flex"
        )
        return response.output_text


    def process_tooled(self, contents: List[str], tools: list[LLMTool] = None) -> str:
        # prepare tools
        prepared_tools = self._prepare_tools(tools)
        system_prompt: EasyInputMessageParam = {
                "role": "system",
                "content": self._prepare_contents(contents),
                "type": "message"
            }

        llm_contents: ResponseInputParam = [system_prompt]

        openai_tools = [t["openai"] for t in prepared_tools.values()]

        responses = []
        while True:
            # 4. Issue a request to Gemini with tools allowed
            response = self.client.responses.create(
                model=self.model_name,
                input=llm_contents,
                tools=openai_tools,
                service_tier="flex",
            )

            llm_contents += response.output

            # Model will either return text or a tool call
            has_tool = False
            for output in response.output:
                if output.type == "tool_calls":
                    has_tool = True
                    responses.append(f"Function Call: {output.name}({output.arguments})")
                    function_result = prepared_tools[output.name]["function"](json.loads(output.arguments))

                    function_call_output: FunctionCallOutput = {
                        "type": "function_call_output",
                        "call_id": output.call_id,
                        "output": json.dumps({
                            output.name: function_result
                        })
                    }
                    llm_contents.append(function_call_output)
                else:
                    responses.append(output)

            if not has_tool:
                break

        return "\n".join(responses)

    def _prepare_contents(self, contents: list[str]) -> str:
        return "\n".join(contents)


    def _prepare_tools(self, tools: list[LLMTool] = None) -> dict:
        prepared_tools = {}
        if tools is None:
            return prepared_tools
        for tool in tools:
            prepared_tools[tool.name] = {
                "function": tool.execute,
                "openai": {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
        return prepared_tools
