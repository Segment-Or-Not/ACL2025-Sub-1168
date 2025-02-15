from openai import OpenAI
from typing import Optional, Dict, Iterable, Any
import logging
import time
import os


class LoggerClient:

    log_folder = "log/log_llm_calls_openai/"

    def __init__(self):

        os.makedirs(self.log_folder, exist_ok=True)
        log_file_name = self.log_folder + f"log_file_{time.time()}.log"

        logging.basicConfig(filename=log_file_name, level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI()

    def chat_completions(
        self,
        model: str,
        messages: Iterable[Dict[str, Any]],
        temperature: Optional[float] = None,
        **params,
    ):
        
        self.logger.info("messages: %s", messages)
        self.logger.info("temperature: %s", str(temperature))
        output = self.client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, **params
        )
        self.logger.info("Output: %s", output.choices[0].message.content)
        return output

default_client = LoggerClient()
chat_completions = default_client.chat_completions

if __name__ == "__main__":
    completion = default_client.chat_completions(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a haiku about recursion in programming."
            }
        ],
        temperature=1
    )

    print(completion.choices[0].message.content)