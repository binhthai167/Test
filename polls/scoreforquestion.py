import re
from spellchecker import SpellChecker


spell = SpellChecker(language=None)
spell.word_frequency.load_text_file("vietnamese_dict.txt")


def score_open_ended_answer(answer_text, question):
    if not answer_text or not question:
        return 0
    max_score = question.max_score
    clean_answer = re.sub(r'[^\w\s]', '', answer_text.lower())
    words = clean_answer.split()
    if not words:  # không có từ nào
        return 0
    unique_words = set(words)
    misspelled = spell.unknown(unique_words)
    spell_penalty = 0.5 * len(misspelled)



    final_score = max_score - spell_penalty
    final_score = max(0, min(final_score, max_score))  # Đảm bảo điểm không âm và không vượt quá max_score
    return final_score
    
