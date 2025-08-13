import re, os
from nltk.tokenize import sent_tokenize
import openai
import nltk
from dotenv import load_dotenv

nltk.download('punkt')
nltk.download('punkt_tab')

load_dotenv()  # Load biến môi trường từ file .env
api_key = os.getenv('OPENAI_API_KEY')
def score_open_ended_answer(answer_text, question):
    if not answer_text or not question:
        return 0

    max_score = question.max_score

    # 1. Tính điểm truyền thống (dựa trên từ khóa, cấu trúc)
    clean_answer = re.sub(r'[^\w\s]', '', answer_text.lower())
    sentences = sent_tokenize(answer_text)
    keywords = [kw.strip().lower() for kw in (question.keywords or "").split(",") if kw.strip()]
    matched_keywords = sum(1 for kw in keywords if kw in clean_answer)
    sentence_count = len(sentences)
    valid_word_count = matched_keywords
    max_needed_keywords = 2

    keyword_score = min(matched_keywords / max_needed_keywords, 1) * 0.5 * max_score
    length_score = min(valid_word_count / 20, 1) * 0.3 * max_score
    structure_score = min(sentence_count / 3, 1) * 0.2 * max_score
    nltk_score = keyword_score + length_score + structure_score

    # 2. Gọi OpenAI API chấm điểm (không cần đáp án mẫu)
    prompt = f"""
Bạn là giáo viên giúp chấm điểm bài kiểm tra tiếng Việt.
Câu hỏi: {question.question_text}
Câu trả lời của học sinh: {answer_text}
Hãy chấm điểm trên thang {max_score} dựa trên mức độ trả lời đúng, rõ ràng, đầy đủ ý, và chính tả.
Chỉ trả về số điểm thập phân (ví dụ 3.5 hoặc 4).
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là giáo viên chấm bài."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        score_text = response.choices[0].message.content.strip()
        openai_score = float(score_text)
        openai_score = max(0, min(openai_score, max_score))
    except Exception as e:
        print("Lỗi khi gọi OpenAI API:", e)
        openai_score = 0

    # 3. Tổng điểm = điểm nltk + điểm openai, giới hạn max_score
    total_score = min(nltk_score + openai_score, max_score)
    return total_score
