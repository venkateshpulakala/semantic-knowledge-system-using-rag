// ============================================
// 1. HTML ELEMENTS
// ============================================

const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const messages = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");

const fileInput = document.getElementById("fileInput");

const uploadPreview = document.getElementById("uploadPreview");
const selectedFileName = document.getElementById("selectedFileName");

const documentList = document.getElementById("documentList");

const newChatBtn = document.getElementById("newChatBtn");
const chatMenu = document.getElementById("chatMenu");
const documentsMenu = document.getElementById("documentsMenu");

const API_BASE_URL = "";


// ============================================
// 2. DISPLAY USER MESSAGE
// ============================================

function addMessage(text, sender) {

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    contentDiv.textContent = text;

    messageDiv.appendChild(contentDiv);
    messages.appendChild(messageDiv);

    scrollToBottom();
}


// ============================================
// 3. DISPLAY AI ANSWER
// ============================================

function addAssistantMessage(answer, sources = []) {

    const messageDiv = document.createElement("div");
    messageDiv.className = "message assistant";

    const avatar = document.createElement("div");
    avatar.className = "ai-avatar";
    avatar.textContent = "✦";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const answerText = document.createElement("div");
    answerText.textContent = answer;

    contentDiv.appendChild(answerText);

    if (sources.length > 0) {

        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources";

        const heading = document.createElement("h4");
        heading.textContent = "📚 Sources";

        sourcesDiv.appendChild(heading);

        const seen = new Set();

        sources.forEach(source => {

            const filename = source.document || source.source;
            const page = source.page;

            const key = `${filename}_${page}`;

            if (seen.has(key)) return;

            seen.add(key);

            const sourceItem = document.createElement("span");
            sourceItem.className = "source-item";

            sourceItem.textContent =
                `📄 ${filename} | Page ${page}`;

            sourcesDiv.appendChild(sourceItem);

        });

        contentDiv.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messages.appendChild(messageDiv);

    scrollToBottom();
}


// ============================================
// 4. LOADING INDICATOR
// ============================================

function showLoading() {

    const loadingDiv = document.createElement("div");

    loadingDiv.className = "message assistant";

    const avatar = document.createElement("div");
    avatar.className = "ai-avatar";
    avatar.textContent = "✦";

    const loadingText = document.createElement("div");
    loadingText.className = "typing-indicator";
    loadingText.textContent = "Thinking...";

    loadingDiv.appendChild(avatar);
    loadingDiv.appendChild(loadingText);

    messages.appendChild(loadingDiv);

    scrollToBottom();

    return loadingDiv;
}


// ============================================
// 5. SCROLL CHAT
// ============================================

function scrollToBottom() {

    const chatContainer =
        document.getElementById("chatContainer");

    chatContainer.scrollTop = chatContainer.scrollHeight;
}


// ============================================
// 6. ASK QUESTION
// ============================================

async function sendQuestion() {

    const question = questionInput.value.trim();

    if (!question) return;

    addMessage(question, "user");

    questionInput.value = "";
    questionInput.style.height = "38px";

    welcomeScreen.style.display = "none";

    const loadingMessage = showLoading();

    sendBtn.disabled = true;

    try {

        const response = await fetch(`${API_BASE_URL}/ask`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Unable to get an answer.");
        }

        loadingMessage.remove();

        addAssistantMessage(
            result.answer,
            result.sources || []
        );

    }

    catch (error) {

        loadingMessage.remove();

        addAssistantMessage(
            "Something went wrong: " + error.message
        );

        console.error("Question error:", error);

    }

    finally {

        sendBtn.disabled = false;
        questionInput.focus();

    }
}


// ============================================
// 7. LOAD DOCUMENTS FROM BACKEND
// ============================================

// ============================================
// LOAD DOCUMENTS FROM BACKEND
// ============================================

async function loadDocuments() {
    try {
        console.log("Loading documents...");

        const response = await fetch("/documents");

        if (!response.ok) {
            throw new Error("Failed to load documents");
        }

        const result = await response.json();

        console.log("Documents API response:", result);

        documentList.innerHTML = "";

        if (!result.documents || result.documents.length === 0) {
            documentList.innerHTML =
                `<p class="empty-documents">No documents uploaded yet.</p>`;
            return;
        }

        result.documents.forEach(doc => {

            const documentItem = document.createElement("div");
            documentItem.className = "document-item";

            // PDF filename
            const filename = document.createElement("span");
            filename.className = "document-filename";
            filename.textContent = "📄 " + doc.filename;

            // Delete button
            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-document-btn";
            deleteButton.textContent = "🗑";
            deleteButton.title = "Delete document";
            deleteButton.type = "button";

            deleteButton.addEventListener("click", async () => {

                const confirmDelete = confirm(
                    `Are you sure you want to delete ${doc.filename}?`
                );

                if (!confirmDelete) return;

                await deleteDocument(doc.filename);
            });

            documentItem.appendChild(filename);
            documentItem.appendChild(deleteButton);

            documentList.appendChild(documentItem);
        });

        console.log("Documents displayed successfully.");

    } catch (error) {
        console.error("Document loading error:", error);

        documentList.innerHTML =
            `<p class="empty-documents">Unable to load documents.</p>`;
    }
}


// ============================================
// DELETE DOCUMENT
// ============================================

async function deleteDocument(filename) {

    try {

        const response = await fetch(
            `/documents/${encodeURIComponent(filename)}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Document deletion failed");
        }

        alert("Document deleted successfully!");

        // Refresh document list
        await loadDocuments();

    }

    catch (error) {

        console.error("Delete error:", error);

        alert("Error deleting document: " + error.message);

        await loadDocuments();

    }

}


// ============================================
// 8. UPLOAD PDF
// ============================================

async function uploadDocument(file) {

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {

        alert("Only PDF files are supported.");

        fileInput.value = "";

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    selectedFileName.textContent = `Uploading: ${file.name}`;

    uploadPreview.style.display = "block";

    const loadingMessage = showLoading();

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const responseText = await response.text();

        console.log("Upload status:", response.status);
        console.log("Upload response:", responseText);

        let result;

        try {

            result = JSON.parse(responseText);

        }

        catch {

            throw new Error(
                "Backend returned an empty or invalid response."
            );

        }

        if (!response.ok) {

            throw new Error(
                result.detail || "Document upload failed."
            );

        }

        loadingMessage.remove();

        addAssistantMessage(
            `Document uploaded successfully!\n\n` +
            `Filename: ${result.filename}\n` +
            `Pages: ${result.total_pages}\n` +
            `Chunks: ${result.total_chunks}`
        );

        // Refresh sidebar documents
        await loadDocuments();

    }

    catch (error) {

        loadingMessage.remove();

        console.error("Upload error:", error);

        addAssistantMessage(
            "Upload failed: " + error.message
        );

    }

    finally {

        fileInput.value = "";

        selectedFileName.textContent = "";

        uploadPreview.style.display = "none";

    }
}


// ============================================
// 9. NEW CHAT
// ============================================

function startNewChat() {

    messages.innerHTML = "";

    welcomeScreen.style.display = "block";

    questionInput.value = "";

    questionInput.style.height = "38px";

    selectedFileName.textContent = "";

    document.getElementById("chatContainer").scrollTop = 0;
}


// ============================================
// 10. EVENT LISTENERS
// ============================================

sendBtn.addEventListener("click", sendQuestion);


questionInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendQuestion();

    }

});


fileInput.addEventListener("change", function() {

    const file = fileInput.files[0];

    uploadDocument(file);

});


newChatBtn.addEventListener("click", startNewChat);


document.querySelectorAll(".suggestion-card").forEach(button => {

    button.addEventListener("click", function() {

        questionInput.value = this.textContent.trim();

        sendQuestion();

    });

});


chatMenu.addEventListener("click", function() {

    chatMenu.classList.add("active");

    documentsMenu.classList.remove("active");

});


documentsMenu.addEventListener("click", function() {

    documentsMenu.classList.add("active");

    chatMenu.classList.remove("active");

    documentList.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

});


// ============================================
// 11. TEXTAREA AUTO RESIZE
// ============================================

questionInput.addEventListener("input", function() {

    this.style.height = "38px";

    this.style.height =
        Math.min(this.scrollHeight, 150) + "px";

});


// ============================================
// 12. INITIALIZE APPLICATION
// ============================================

document.addEventListener("DOMContentLoaded", function() {

    loadDocuments();

    console.log(
        "Semantic Knowledge System frontend loaded successfully!"
    );

});