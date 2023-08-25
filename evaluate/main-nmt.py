from src.models.nmt.gpt_model import OpenAITranslator
from src.models.nmt.envit5_model import EnVit5Translator
from src.utils.metric import Metric


if __name__=="__main__":
    text = "We're on a journey to advance and democratize artificial intelligence through open source and open science."
    gt = "Chúng tôi đang trên hành trình thúc đẩy và dân chủ hóa trí tuệ nhân tạo thông qua mã nguồn mở và khoa học mở."

    translator = OpenAITranslator()
    # translator = EnVit5Translator()
    translated_text, execution_time = translator.translate(text)
    
    bleu_score = Metric.calculate_bleu_score(gt, translated_text)
    memory_usage = Metric.calculate_memory_usage()

    print("Translated Text:", translated_text)
    print("Execution Time:", execution_time, "seconds")
    print("BLEU Score:", bleu_score)
    print("Memory Usage:", memory_usage, "MB")