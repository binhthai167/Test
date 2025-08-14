import re, os
from spellchecker import SpellChecker
from sentence_transformers import SentenceTransformer, util


# nltk.download('punkt')
# nltk.download('punkt_tab')
spell = SpellChecker(language=None)
spell.word_frequency.load_text_file("vietnamese_dict.txt")

# 2. Khởi tạo mô hình sentence embedding
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # hỗ trợ tiếng Việt

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
    
     # --- Kiểm tra ngữ nghĩa ---
    embeddings = model.encode([answer_text, question.keywords])
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()  # từ 0 tới 1
    
    semantic_score = max_score * similarity

    if semantic_score > 0.3 * max_score:
        semantic_score = max_score  # nếu điểm ngữ nghĩa lớn hơn 30% max_score, thì cho điểm tối đa
    final_score = semantic_score - spell_penalty
    final_score = max(0, min(final_score, max_score))  # Đảm bảo điểm không âm và không vượt quá max_score
    return final_score
    # sentences = sent_tokenize(answer_text)
    # keywords = [kw.strip().lower() for kw in (question.keywords or "").split(",") if kw.strip()]
    # matched_keywords = sum(1 for kw in keywords if kw in clean_answer)
    # sentence_count = len(sentences)
    # valid_word_count = matched_keywords
    # max_needed_keywords = 2

    # keyword_score = min(matched_keywords / max_needed_keywords, 1) * 0.9 * max_score
    # length_score = min(valid_word_count / 5, 1) * 0.1 * max_score

    # nltk_score = keyword_score + length_score 

    # return nltk_score
