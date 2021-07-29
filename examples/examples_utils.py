import time
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language


def log_exceptions(func):
    def function_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            with open("../logs/log.txt", "a") as f:
                f.write(f'{args[0]}\t{type(e).__name__}\n')
            return 0

    return function_wrapper


def timing(func):
    def function_wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print("--- {:.1f} seconds ---".format(time.time() - start_time))

    return function_wrapper


@Language.factory('language_detector')
def language_detector(nlp, name):
    return LanguageDetector()


def set_nlp_model():
    nlp = spacy.load('en_core_web_sm')
    nlp.max_length = 2000000
    nlp.add_pipe('language_detector', last=True)
    return nlp