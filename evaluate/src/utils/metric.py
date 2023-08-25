import psutil
import time
from nltk.translate.bleu_score import sentence_bleu
import Levenshtein as lev


class Metric:

    def __init__(self): 
        pass 
        
    @staticmethod
    def calculate_memory_usage():
        process = psutil.Process()
        return process.memory_info().rss / (1024 ** 2)

    @staticmethod
    def calculate_bleu_score(reference, translation):
        reference = reference.split()  # Convert reference sentence to list of words
        translation = translation.split()  # Convert generated translation to list of words
        return sentence_bleu([reference], translation,  weights=(0.33, 0.33, 0.34))

    @staticmethod
    def cer(reference, hypothesis):
        """
        Calculation of CER with Levenshtein distance.

        Arguments:
        reference -- the reference string
        hypothesis -- the hypothesis string
        """
        # Initialize counter variables
        substitution, insertion, deletion = 0, 0, 0

        # Compute the Levenshtein distance and the length of reference
        distance = lev.distance(reference, hypothesis)
        length = len(reference)

        return distance / length
