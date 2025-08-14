
    document.querySelectorAll("#submitAns input").forEach(input => {
    // Khi input không hợp lệ
    input.addEventListener("invalid", function (event) {
        event.preventDefault(); // Ngăn thông báo mặc định
        if (!input.validity.valid) {
            input.setCustomValidity(input.dataset.error); // Lấy thông báo từ data-error
        } else {
            input.setCustomValidity("");
        }
        input.reportValidity();
    });
    // Khi input hợp lệ
        input.addEventListener("input", function () {
        input.setCustomValidity("");
    });
});
// Hàm debounce: chỉ thực hiện sau khi người dùng dừng gõ wait ms
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
   
    // Hàm lấy CSRF token từ cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        console.log("CSRF Token:", cookieValue); // Debug CSRF token
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Lưu câu trả lời văn bản
    document.querySelectorAll('textarea.input-textarea').forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            const questionId = this.name.replace('question_', '');
            const answerText = this.value;
            saveTextAnswer(questionId, answerText);
        });
        // Khởi tạo: Gửi lại câu trả lời đã lưu từ session (nếu có) khi tải trang
        // const questionId = textarea.name.replace('question_', '');
        // if (textarea.value) {
        //     saveTextAnswer(questionId, textarea.value);
        // }
    });

    // Lưu câu trả lời trắc nghiệm
    document.querySelectorAll('input[type=radio]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            const questionId = this.name.replace('question_', '');
            const choiceId = this.value;
            saveChoice(questionId, choiceId);
        });
    });

    // Hàm lưu câu trả lời văn bản qua AJAX
    function saveTextAnswer(questionId, answerText) {
        console.log("Saving text answer for question:", questionId, "Answer:", answerText);
        fetch("{% url 'polls:save_text_answer' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: "question_id=" + encodeURIComponent(questionId) +
                  "&answer_text=" + encodeURIComponent(answerText)
        })
        .then(response => {
            console.log("Save text response status:", response.status);
            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                console.log("Text answer saved successfully:", data);
                // Lưu vào localStorage như dự phòng
            } else {
                console.error("Error saving text answer:", data.message);
                alert("Lỗi khi lưu câu trả lời văn bản: " + data.message);
                localStorage.setItem('text_answer_' + questionId, answerText);
            }
        })
        .catch(error => {
            console.error("Error in saveTextAnswer:", error);
            localStorage.setItem('text_answer_' + questionId, answerText);
        });
    }

    // Hàm lưu câu trả lời trắc nghiệm qua AJAX
    function saveChoice(questionId, choiceId) {
        console.log("Saving choice for question:", questionId, "Choice:", choiceId);
        fetch("{% url 'polls:save_choice' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: "question_id=" + encodeURIComponent(questionId) +
                  "&choice_id=" + encodeURIComponent(choiceId)
        })
        .then(response => {
            console.log("Save choice response status:", response.status);
            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                console.log("Choice saved successfully:", data);
            } else {
                console.error("Error saving choice:", data.message);
                alert("Lỗi khi lưu câu trả lời trắc nghiệm: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error in saveChoice:", error);
            alert("Lỗi kết nối khi lưu câu trả lời trắc nghiệm.");
        });
    }

    // Xử lý redirect khi đã hoàn thành bài thi
    const examCompletedStr = "{{ exam_completed|default_if_none:'false' }}";
    const examCompleted = examCompletedStr.toLowerCase() === "true";

    if (examCompleted) {
        window.location.replace("{% url 'polls:result' exam_code.code %}");
    }

    // Xử lý khi trang được load từ bộ nhớ cache của trình duyệt
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            window.location.replace("{% url 'polls:result' exam_code.code %}");
        }
    });

    // Lưu câu trả lời trước khi trang được tải lại hoặc đóng
    window.addEventListener('beforeunload', function(event) {
        document.querySelectorAll('textarea.input-textarea').forEach(function(textarea) {
            const questionId = textarea.name.replace('question_', '');
            const answerText = textarea.value;
            if (answerText) {
                console.log("Before unload: Saving text answer for question:", questionId);
                saveTextAnswer(questionId, answerText);
            }
        });
        document.querySelectorAll('input[type=radio]:checked').forEach(function(radio) {
            const questionId = radio.name.replace('question_', '');
            const choiceId = radio.value;
            console.log("Before unload: Saving choice for question:", questionId);
            saveChoice(questionId, choiceId);
        });
    });

    // Tự động lưu câu trả lời mỗi 5 giây
    setInterval(function() {
        document.querySelectorAll('textarea.input-textarea').forEach(function(textarea) {
            const questionId = textarea.name.replace('question_', '');
            const answerText = textarea.value;
            if (answerText) {
                console.log("Periodic save: Saving text answer for question:", questionId);
                saveTextAnswer(questionId, answerText);
            }
        });
        document.querySelectorAll('input[type=radio]:checked').forEach(function(radio) {
            const questionId = radio.name.replace('question_', '');
            const choiceId = radio.value;
            console.log("Periodic save: Saving choice for question:", questionId);
            saveChoice(questionId, choiceId);
        });
    }, 5000); // Lưu mỗi 5 giây

    // Khôi phục câu trả lời từ localStorage khi tải trang
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('textarea.input-textarea').forEach(function(textarea) {
            const questionId = textarea.name.replace('question_', '');
            const savedAnswer = localStorage.getItem('text_answer_' + questionId);
            if (savedAnswer && !textarea.value) {
                console.log("Restoring text answer from localStorage for question:", questionId);
                textarea.value = savedAnswer;
                saveTextAnswer(questionId, savedAnswer); // Gửi lại lên server
            }
        });
    });
