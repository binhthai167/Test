import re
from spellchecker import SpellChecker
import math

spell = SpellChecker(language=None)
spell.word_frequency.load_text_file("vietnamese_dict.txt")


def score_open_ended_answer(answer_text, question):
    if not answer_text or not question or len(answer_text.strip()) < 3:
        return 0
    max_score = question.max_score
    clean_answer = re.sub(r'[^\w\s]', '', answer_text.lower())
    words = clean_answer.split()
    if not words:  # không có từ nào
        return 0
    unique_words = set(words)
    misspelled = spell.unknown(unique_words)
    spell_penalty = 0.5 * len(misspelled)

    similarity = cosine_similarity(answer_text, question.keywords)
    similarity_score = similarity * max_score
    if similarity > 0.3 :
        similarity_score = max_score
    final_score = similarity_score - spell_penalty
    final_score = max(0, min(final_score, max_score))  # Đảm bảo điểm không âm và không vượt quá max_score
    return final_score



def cosine_similarity(text1, text2):
    # Tokenize
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    all_words = list(set(words1) | set(words2))

    # Tạo vector đếm từ
    vec1 = [words1.count(w) for w in all_words]
    vec2 = [words2.count(w) for w in all_words]

    # Tính tích vô hướng & độ dài vector
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)
    
