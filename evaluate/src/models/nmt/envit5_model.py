from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import time

class EnVit5Translator:
    def __init__(self, model_name: str = "VietAI/envit5-translation"):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def translate(self, inputs):
        """
        Translates input text using the model.
        
        Args:
            inputs (str): The text to be translated.
        
        Returns:
            tuple: A tuple containing the translated text (str) and the time taken for translation (float).
        """
        start_time = time.time()
        input_ids = self.tokenizer(inputs, return_tensors="pt", padding=True).input_ids.to(self.device)
        outputs = self.model.generate(input_ids, max_length=512)
        translated_text = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0][4:]
        return translated_text, time.time() - start_time
