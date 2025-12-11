import logging
import threading
from datetime import datetime
from typing import List, Callable
from PIL.Image import Image
from dependency_injector.wiring import inject, Provide
from google import genai
from google.genai import types

from traitor.core.data.models import TokenUsage
from traitor.core.tools.ai.llm_agent import LLMAgent
from traitor.core.tools.ai.llm_tools import LLMTool


class LLMGemini(LLMAgent):
    name = "Gemini"
    @inject
    def __init__(self, model: str = 'gemini-2.5-flash', api_key=Provide["config.api_keys.GEMINI"]):
        self.model_name = model
        self.client = genai.Client(api_key=api_key)
        super().__init__()

    def process_text(self, contents: list[str], prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        llm_content = self._prepare_contents(contents)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=llm_content,
        )
        self.token_usage_repo.add(TokenUsage(
            time=datetime.now(),
            # prompt_token_count includes the cached token count, but we want to separate
            input_tokens=response.usage_metadata.prompt_token_count - response.usage_metadata.cached_content_token_count,
            cached_tokens=response.usage_metadata.cached_content_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
            reasoning_tokens=response.usage_metadata.thoughts_token_count,
            tool_tokens=response.usage_metadata.tool_use_prompt_token_count,
            total_tokens=response.usage_metadata.total_token_count,
            api=self.name,
            agent=threading.current_thread().name,
            model=self.model_name,
            comment=usage_comment,
        ))
        return response.text

    def process_tooled(self, contents: List[str], tools: list[LLMTool] = None, prompt_cache_key: str | None = None, usage_comment: str | None = None) -> str:
        # prepare tools
        prepared_tools = self._prepare_tools(tools)
        llm_contents: types.ContentListUnionDict = self._prepare_contents(contents)

        gemini_tools = types.Tool(function_declarations=[t["description"] for t in prepared_tools.values()])
        config = types.GenerateContentConfig(tools=[gemini_tools])
        token_usage = TokenUsage(
            time=datetime.now(),
            input_tokens=0,
            cached_tokens=0,
            output_tokens=0,
            reasoning_tokens=0,
            tool_tokens=0,
            total_tokens=0,
            api=self.name,
            agent=threading.current_thread().name,
            model=self.model_name,
            comment=usage_comment,
        )
        responses = []
        while True:
            # 4. Issue a request to Gemini with tools allowed
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=llm_contents,
                config=config,
            )

            # count tokens
            token_usage.input_tokens += response.usage_metadata.prompt_token_count - response.usage_metadata.cached_content_token_count
            token_usage.cached_tokens += response.usage_metadata.cached_content_token_count
            token_usage.output_tokens += response.usage_metadata.candidates_token_count
            token_usage.reasoning_tokens += response.usage_metadata.thoughts_token_count
            token_usage.tool_tokens += response.usage_metadata.tool_use_prompt_token_count
            token_usage.total_tokens += response.usage_metadata.total_token_count


            calling_functions = False
            # Check for a function call
            content = response.candidates[0].content
            parts = content.parts
            for part in parts:
                if part.function_call:
                    calling_functions = True
                    function_call = part.function_call
                    logging.debug(f"Function to call: {function_call.name}")
                    logging.debug(f"Arguments: {function_call.args}")
                    responses.append(f"Function Call: {function_call.name}({function_call.args})")

                    # Actually call the function
                    result = prepared_tools[function_call.name]["function"](**function_call.args)
                    function_response_part = types.Part.from_function_response(
                        name=function_call.name,
                        response={"result": result},
                    )
                    llm_contents.append(content) # Append the content from the model's response.
                    llm_contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response
                else:
                    responses.append(response.text)

            # run as long as the LLM wants to call functions
            if not calling_functions:
                break
        self.token_usage_repo.add(token_usage)
        return "\n".join(responses)


    def _prepare_contents(self, contents: list[str]) -> types.ContentListUnionDict:
        return [types.Part.from_text(text=c) for c in contents]


    def _prepare_tools(self, tools: list[LLMTool] = None) -> dict:
        prepared_tools = {}
        if tools is None:
            return prepared_tools
        for tool in tools:
            prepared_tools[tool.name] = {
                "function": tool.execute,
                "description": tool.to_dict(),
            }
        return prepared_tools

    def process_image(self, image: Image, context: List[str]) -> str:
        content = []
        content.extend(context)
        content.append(image)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=content,
        )
        response.resolve()
        return response.text
