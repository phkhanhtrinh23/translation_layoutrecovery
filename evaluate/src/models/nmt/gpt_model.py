import time
import os
import psutil

import openai
from dotenv import load_dotenv
from nltk.translate.bleu_score import sentence_bleu

from src.utils.metric import Metric

load_dotenv()

class OpenAITranslator:
    def __init__(self, engine="text-davinci-002"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.engine = engine
        openai.api_key = self.api_key

    def translate(self, text):
        """
        Translates the given text to Vietnamese using the OpenAI translation API.

        Parameters:
            text (str): The text to be translated.

        Returns:
            tuple: A tuple containing the translated text (str) and the execution time (float).
        """
        start_time = time.time()

        response = openai.Completion.create(
            engine=self.engine,
            prompt=f"Translate the following text to Vietnamese: {text}",
            max_tokens=1000
        )

        translated_text = response.choices[0].text.strip()
        end_time = time.time()
        execution_time = end_time - start_time

        return translated_text, execution_time


