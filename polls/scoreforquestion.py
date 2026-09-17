import re
from spellchecker import SpellChecker
import math

spell = SpellChecker(language=None)
has_dict = False
try:
    spell.word_frequency.load_text_file("vietnamese_dict.txt")
    has_dict = True # Nếu có file từ điển thì mới bật kiểm tra chính tả
except FileNotFoundError:
    pass

def score_open_ended_answer(answer_text, question, exam_code=None):
    if not answer_text or not question:
        return 0
        
    answer_text_lower = answer_text.lower()
    max_score = question.max_score
    
    # 1. GOM Ý TỪ CORRECT ANSWER & KEYWORDS
    all_ideas = []
    if question.correct_answer:
        all_ideas.extend([line.strip().lower() for line in question.correct_answer.split('\n') if line.strip()])
        
    if hasattr(question, 'keywords') and question.keywords:
        all_ideas.extend([k.strip().lower() for k in question.keywords.split(',') if k.strip()])
        
    # 2. TÍNH ĐIỂM DỰA TRÊN TỪ KHÓA & TỪ ĐỒNG NGHĨA (DẤU |)
    num_ideas = len(all_ideas)
    score = 0.0
    
    if num_ideas > 0:
        points_per_idea = max_score / num_ideas
        for idea_group in all_ideas:
            # Tách từ đồng nghĩa
            synonyms = [s.strip() for s in idea_group.split('|') if s.strip()]
            if any(synonym in answer_text_lower for synonym in synonyms):
                score += points_per_idea
    else:
        # Nếu câu hỏi mở hoàn toàn (không có từ khóa), tạm cho điểm tối đa
        score = max_score

    # 3. KIỂM TRA LỖI CHÍNH TẢ 
    # Chỉ trừ điểm nếu là Bài Đầu Vào VÀ máy tính có file từ điển
    if exam_code != 'SAU_DAO_TAO_01' and has_dict:
        clean_answer = re.sub(r'[^\w\s]', '', answer_text_lower)
        words = clean_answer.split()
        if words:
            unique_words = set(words)
            misspelled = spell.unknown(unique_words)
            spell_penalty = 0.5 * len(misspelled)
            score -= spell_penalty

    # Làm tròn và đảm bảo điểm không âm, không vượt max_score
    score = round(score, 2)
    final_score = max(0, min(score, max_score))
    return final_score

def cosine_similarity(text1, text2):
    # (Giữ nguyên như cũ)
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    all_words = list(set(words1) | set(words2))

    vec1 = [words1.count(w) for w in all_words]
    vec2 = [words2.count(w) for w in all_words]

    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)