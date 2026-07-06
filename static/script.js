document.addEventListener("DOMContentLoaded", function() {

    /* ==========================================
       HTML ELEMENTS
    ========================================== */

    const uploadArea = document.getElementById("uploadArea");
    const imageInput = document.getElementById("imageInput");
    const previewContainer = document.getElementById("imagePreviewContainer");
    const preview = document.getElementById("imagePreview");
    const imageName = document.getElementById("imageName");
    const removeBtn = document.getElementById("removeImage");

    const form = document.getElementById("analyzeForm");
    const loadingScreen = document.getElementById("loadingScreen");
    const loadingText = document.getElementById("loadingText");

    const textarea = document.querySelector("textarea");
    const wordCounter = document.getElementById("wordCounter");

    const resultCard = document.getElementById("resultCard");

    const confidenceValue = document.getElementById("confidenceValue");
    const trustFill = document.getElementById("trustFill");

    const explanation = document.getElementById("aiExplanation");

    /* ==========================================
       WORD COUNTER
    ========================================== */

    if (textarea && wordCounter) {
        textarea.addEventListener("input", () => {
            const words = textarea.value
                .trim()
                .split(/\s+/)
                .filter(word => word.length > 0);
            wordCounter.innerHTML = `${words.length} Words`;
        });
    }

    /* ==========================================
       CLICK TO SELECT IMAGE
    ========================================== */

    uploadArea?.addEventListener("click", () => {
        imageInput.click();
    });

    /* ==========================================
       IMAGE SELECTION
    ========================================== */

    imageInput?.addEventListener("change", () => {
        if (imageInput.files.length > 0) {
            showPreview(imageInput.files[0]);
        }
    });

    /* ==========================================
       DRAG & DROP
    ========================================== */

    uploadArea?.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("dragover");
    });

    uploadArea?.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
    });

    uploadArea?.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("dragover");
        const file = e.dataTransfer.files[0];
        if (file) {
            imageInput.files = e.dataTransfer.files;
            showPreview(file);
        }
    });

    /* ==========================================
       IMAGE PREVIEW
    ========================================== */

    function showPreview(file) {
        preview.src = URL.createObjectURL(file);
        previewContainer.style.display = "block";
        preview.style.display = "block";
        imageName.innerHTML = file.name;
    }

    /* ==========================================
       REMOVE IMAGE
    ========================================== */

    removeBtn?.addEventListener("click", () => {
        imageInput.value = "";
        preview.removeAttribute("src"); // safer than empty string
        previewContainer.style.display = "none";
    });

    /* ==========================================
       LOADING SCREEN
    ========================================== */

    form?.addEventListener("submit", () => {
        loadingScreen.style.display = "flex";

        const messages = [
            "🔍 Extracting OCR Text...",
            "🧠 Running Machine Learning Model...",
            "📊 Calculating Confidence Score...",
            "🔎 Detecting Misinformation Patterns...",
            "📑 Generating AI Explanation...",
            "✅ Finalizing Report..."
        ];

        let i = 0;
        loadingText.innerHTML = messages[0];

        const interval = setInterval(() => {
            i++;
            if (i < messages.length) {
                loadingText.innerHTML = messages[i];
            } else {
                clearInterval(interval); // prevent memory leak
            }
        }, 1200);
    });

    /* ==========================================
       AUTO SCROLL
    ========================================== */

    if (resultCard) {
        setTimeout(() => {
            resultCard.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 400);
    }

    /* ==========================================
       CONFIDENCE COUNTER
    ========================================== */

    if (confidenceValue) {
        const target = parseFloat(confidenceValue.dataset.confidence);
        let count = 0;

        const interval = setInterval(() => {
            count++;
            confidenceValue.innerHTML = count;

            if (count >= target) {
                confidenceValue.innerHTML = target.toFixed(2);
                clearInterval(interval);
            }
        }, 15);
    }

    /* ==========================================
       TRUST BAR
    ========================================== */

    if (trustFill) {
        setTimeout(() => {
            trustFill.style.width = trustFill.dataset.width + "%";
        }, 500);
    }

    /* ==========================================
       AI TYPING EFFECT
    ========================================== */

    if (explanation) {
        const text = explanation.dataset.text || "";
        explanation.innerHTML = "";
        let i = 0;

        function typing() {
            if (i < text.length) {
                explanation.innerHTML += text.charAt(i);
                i++;
                setTimeout(typing, 20);
            }
        }

        typing();
    }

});

/* ==========================================
   PAGE LOADED
========================================== */

window.addEventListener("load", () => {
    const loading = document.getElementById("loadingScreen");
    if (loading) {
        loading.style.display = "none";
    }
});
