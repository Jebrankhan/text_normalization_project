
import re
import string
from textblob import TextBlob
from .slang_dict import slang_dict, contractions_dict
from .vocab_loader import vocab
from .context_utils import context_refine
from difflib import get_close_matches

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|@\S+|#\S+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def reduce_repeated_chars(word):
    return re.sub(r"(.)\1{2,}", r"\1", word)

def restore_contractions(text):
    for contr, full in contractions_dict.items():
        text = re.sub(rf"\b{contr}\b", full, text)
    return text

def correct_vowel_removed(word):
    # Tries to restore missing vowels by matching to vocab
    pattern = re.sub(r"[aeiou]", "", word)
    matches = [w for w in vocab if re.sub(r"[aeiou]", "", w) == pattern]
    return matches[0] if matches else word

def correct_spelling(word):
    return str(TextBlob(word).correct())

def phonetic_correction(word):
    candidates = get_close_matches(word, vocab, n=3, cutoff=0.8)
    return candidates[0] if candidates else word

def normalize_sentence(tokens, window=2):
    normalized = []
    for i, w in enumerate(tokens):
        w = reduce_repeated_chars(w)
        if w in slang_dict:
            norm = slang_dict[w]
        elif w in vocab:
            norm = w
        else:
            # Try spelling correction
            corr = correct_spelling(w)
            if corr in vocab:
                norm = corr
            else:
                # Try restoring vowels
                norm = correct_vowel_removed(w)
                if norm not in vocab:
                    # Final fallback: phonetic match
                    norm = phonetic_correction(w)

        norm = context_refine(norm, tokens[max(0,i-window):i] + tokens[i+1:i+1+window])
        normalized.append(norm)
    return normalized

def normalize_text(text):
    text = clean_text(text)
    text = restore_contractions(text)
    for phrase, repl in slang_dict.items():
        if phrase in text:
            text = text.replace(phrase, repl)
    tokens = text.split()
    return " ".join(normalize_sentence(tokens))

