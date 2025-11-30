import os
import google.generativeai as genai
from pydantic import BaseModel
from typing import List, Optional, Any, Type, Callable
import json
import time
import random

class SimpleFunctionTool:
    def __init__(self, func: Callable, name: str = None, description: str = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__

class AgentResult:
    def __init__(self, text: str, value: Any = None, metadata: dict = None):
        self.text = text
        self.result = [type('Result', (), {'value': value})] if value else []
        self.metadata = metadata or {}

class SimpleLlmAgent:
    def __init__(self, model: str, name: str, description: str, instruction: str = "", tools: List[SimpleFunctionTool] = None):
        self.model_name = model
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        
        # Configure genai
        if os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=instruction if instruction else None,
            tools=[t.func for t in self.tools] if self.tools else None
        )

    def act(self, input: str, output_schema: Type[BaseModel] = None) -> AgentResult:
        start_time = time.time()
        generation_config = {}
        if output_schema:
            generation_config['response_mime_type'] = 'application/json'
            # generation_config['response_schema'] = output_schema
        
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            
            response = None
            max_retries = 5
            base_delay = 10
            
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(input, generation_config=generation_config)
                    break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        if attempt < max_retries - 1:
                            wait_time = base_delay * (2 ** attempt) + random.uniform(0, 5)
                            print(f"Rate limit hit. Retrying in {wait_time:.2f}s...")
                            time.sleep(wait_time)
                            continue
                    raise e
            
            if not response:
                raise Exception("Max retries exceeded for rate limit.")
            
            text = response.text
            text = response.text
            
            value = None
            if output_schema:
                try:
                    # Parse JSON
                    json_text = text
                    if "```json" in json_text:
                        json_text = json_text.split("```json")[1].split("```")[0]
                    elif "```" in json_text:
                        json_text = json_text.split("```")[1].split("```")[0]
                    
                    data = json.loads(json_text)
                    value = output_schema(**data)
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
            
            end_time = time.time()
            latency = end_time - start_time
            
            metadata = {
                "latency": latency,
                "tool_calls": [t.name for t in self.tools] if self.tools else [],
                "model": self.model_name
            }
            
            return AgentResult(text, value, metadata)
            
        except Exception as e:
            return AgentResult(f"Error: {e}", metadata={"error": str(e)})
