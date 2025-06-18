
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
    pattern = re.sub(r"[aeiou]", "", word)
    matches = [w for w in vocab if re.sub(r"[aeiou]", "", w) == pattern]
    return matches[0] if matches else word

def correct_spelling(word):
    return str(TextBlob(word).correct())

def phonetic_correction(word):
    candidates = get_close_matches(word, vocab, n=3, cutoff=0.8)
    return candidates[0] if candidates else word

def normalize_text(text):
    text = clean_text(text)
    text = restore_contractions(text)

    # Step 1: Phrase-level slang replacement (e.g., "gd mrng" -> "good morning")
    for phrase, replacement in slang_dict.items():
        if " " in phrase:
            text = text.replace(phrase, replacement)

    tokens = text.split()

    # Step 2: Word-level slang mapping
    tokens = [slang_dict.get(w, w) for w in tokens]

    # Step 3: Remaining corrections
    normalized = []
    for i, w in enumerate(tokens):
        if w in vocab:
            normalized.append(w)
            continue

        w = reduce_repeated_chars(w)
        corr = correct_spelling(w)
        if corr in vocab:
            norm = corr
        else:
            norm = correct_vowel_removed(w)
            if norm not in vocab:
                norm = phonetic_correction(w)

        norm = context_refine(norm, tokens[max(0, i-2):i] + tokens[i+1:i+3])
        normalized.append(norm)

    return " ".join(normalized)
