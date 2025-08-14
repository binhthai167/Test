
import re
with open("book.txt", "r", encoding="utf-8") as f:
    text = f.read().lower()
clean_text = re.sub(r'[^a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệìỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ\s]', '', text)
words = clean_text.split()
unique_words = set(words)
with open("vietnamese_dict.txt", "w", encoding="utf-8") as f:
    for word in sorted(unique_words):
        f.write(word + "\n")