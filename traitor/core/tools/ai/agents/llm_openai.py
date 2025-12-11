import json
import logging
from datetime import datetime
from typing import List, Union

from dependency_injector.wiring import inject, Provide
from openai import OpenAI, omit
from openai.types.responses import ResponseInputParam, EasyInputMessage, EasyInputMessageParam
from openai.types.responses.response_input_param import FunctionCallOutput

from traitor.core.data.models import TokenUsage
from traitor.core.tools.ai.llm_agent import LLMAgent
from traitor.core.tools.ai.llm_tools import LLMTool


class LLMOpenAI(LLMAgent):
    name = "OpenAI"

    @inject
    def __init__(self, model: str = "gpt-5-nano", api_key: str = Provide["config.api_keys.OPENAI"]):
        self.model_name = model
        self.client = OpenAI(api_key=api_key)
        super().__init__()

    def process_text(self, contents: List[str], prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            input=self._prepare_contents(contents),
            prompt_cache_key=prompt_cache_key if prompt_cache_key is not None else omit,
            service_tier="flex"
        )
        self.token_usage_repo.add(TokenUsage(
            time=datetime.now(),
            input_tokens=response.usage.input_tokens,
            cached_tokens=response.usage.input_tokens_details.cached_tokens,
            output_tokens=response.usage.output_tokens,
            reasoning_tokens=response.usage.output_tokens_details.reasoning_tokens,
            api=self.name,
            model=self.model_name,
            comment=usage_comment,
        ))
        return response.output_text


    def process_tooled(self, contents: List[str], tools: list[LLMTool] = None, prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        # prepare tools
        prepared_tools = self._prepare_tools(tools)
        system_prompt: EasyInputMessageParam = {
                "role": "system",
                "content": self._prepare_contents(contents),
                "type": "message"
            }

        llm_contents: ResponseInputParam = [system_prompt]

        openai_tools = [t["openai"] for t in prepared_tools.values()]

        token_usage = TokenUsage(
            time=datetime.now(),
            input_tokens=0,
            cached_tokens=0,
            output_tokens=0,
            reasoning_tokens=0,
            api=self.name,
            model=self.model_name,
            comment=usage_comment,
        )

        responses = []
        while True:
            # 4. Issue a request to Gemini with tools allowed
            response = self.client.responses.create(
                model=self.model_name,
                input=llm_contents,
                tools=openai_tools,
                prompt_cache_key=prompt_cache_key if prompt_cache_key is not None else omit,
                service_tier="flex",
            )

            # update token_usage
            token_usage.input_tokens +=response.usage.input_tokens
            token_usage.cached_tokens += response.usage.input_tokens_details.cached_tokens
            token_usage.output_tokens += response.usage.output_tokens
            token_usage.reasoning_tokens += response.usage.output_tokens_details.reasoning_tokens

            # Model will either return text or a tool call
            has_tool = False
            for output in response.output:
                if output.type == "function_call":
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

        self.token_usage_repo.add(token_usage)
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
