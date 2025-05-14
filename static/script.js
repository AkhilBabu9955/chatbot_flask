function toggleChat() {
    let chatBox = document.getElementById("chatBox");
    chatBox.style.display = chatBox.style.display === "block" ? "none" : "block";

    // If chatbot is opening for the first time, send initial message
    if (chatBox.style.display === "block" && document.getElementById("chatBody").innerHTML.trim() === "") 
        ;
    
}

function sendMessage() {
    let userInput = document.getElementById("userInput").value.trim();
    if (!userInput) return;

    showMessage("You", userInput);

    // Send request to backend
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        showMessage("Bot", data.response);
    });

    document.getElementById("userInput").value = "";
}

// Function to display messages
function showMessage(sender, message) {
    let chatBody = document.getElementById("chatBody");
    let messageDiv = document.createElement("div");
    messageDiv.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;  // Auto-scroll
}

// Handle enter key press
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
