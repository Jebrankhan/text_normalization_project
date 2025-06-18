
from textblob import TextBlob
import re
from .slang_dict import slang_dict
from .vocab_loader import vocab
from .context_utils import context_refine
from difflib import get_close_matches

def clean_text(text):
    return re.sub(r"http\S+|@\S+|#\S+|[^\w\s]", "", text.lower())

def reduce_repeated_chars(w):
    return re.sub(r"(.)\1{2,}", r"\1", w)

def correct_spelling(word):
    return str(TextBlob(word).correct())

def phonetic_correction(word):
    candidates = get_close_matches(word, vocab, n=3, cutoff=0.8)
    return candidates[0] if candidates else word

def normalize_sentence(tokens, window=2):
    normalized = []
    for i, w in enumerate(tokens):
        w_clean = reduce_repeated_chars(w)
        if w_clean in slang_dict:
            norm = slang_dict[w_clean]
        elif w_clean in vocab:
            norm = w_clean
        else:
            corr1 = correct_spelling(w_clean)
            norm = corr1 if corr1 in vocab else phonetic_correction(w_clean)

        norm = context_refine(norm, tokens[max(0,i-window):i] + tokens[i+1:i+1+window])
        normalized.append(norm)
    return normalized

def normalize_text(text):
    tokens = clean_text(text).split()
    return " ".join(normalize_sentence(tokens))
