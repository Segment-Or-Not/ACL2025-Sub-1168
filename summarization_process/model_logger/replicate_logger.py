import replicate
from typing import Optional, Dict, Any
import logging
import time
import os

class LoggerClient:

    log_folder = "log/log_llm_calls_replicate/"

    def __init__(self):

        os.makedirs(self.log_folder, exist_ok=True)
        log_file_name = self.log_folder + f"log_file_{time.time()}.log"

        logging.basicConfig(filename=log_file_name, level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(
        self,
        ref: str,
        input: Optional[Dict[str, Any]] = None,
        **params,
    ):
        
        self.logger.info("Input: %s", input)
        output = replicate.run(ref, input=input, **params)
        self.logger.info("Output: %s", "".join(output))
        return output
    

default_client = LoggerClient()
run = default_client.run

        
