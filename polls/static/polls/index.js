document.addEventListener('DOMContentLoaded', function() {
    // --- Xử lý input invalid ---
    document.querySelectorAll("#submitAns input").forEach(input => {
        input.addEventListener("invalid", function(event) {
            event.preventDefault();
            if (!input.validity.valid) {
                input.setCustomValidity(input.dataset.error);
            } else {
                input.setCustomValidity("");
            }
            input.reportValidity();
        });
        input.addEventListener("input", function() {
            input.setCustomValidity("");
        });
    });
   
});



document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('submitAns');
    const submitBtn = document.getElementById('submit');

    form.addEventListener('submit', function(e) {
        // Disable button và đổi text
        submitBtn.disabled = true;
        submitBtn.innerText = "Đang nộp...";
    });
});