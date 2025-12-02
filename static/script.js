const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const container = document.getElementById("chat-container");

let messageCount = 0;

// Get username from sessionStorage, fallback to "there"
const username = sessionStorage.getItem("username") || "there";

// Handle chat form submission
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    // Display user's message
    addMessage(message, true);
    input.value = "";
    showTyping();

    try {
        const formData = new URLSearchParams();
        formData.append("message", message);
        formData.append("username", username);

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();
        removeTyping();

        if (data && data.response) {
            addMessage(data.response, false);
        } else {
            addMessage("Sorry, I didn't get a response from the server.", false);
        }
    } catch (err) {
        removeTyping();
        console.error(err);
        addMessage("Sorry, I'm having connection issues. Try again!", false);
    }
});

// Add a chat message to the UI
function addMessage(text, isUser = false) {
    messageCount++;
    const div = document.createElement("div");
    div.className = `message max-w-xs sm:max-w-md lg:max-w-lg px-5 py-3 rounded-2xl break-words ${
        isUser
            ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white ml-auto"
            : "bg-white/20 text-white mr-auto backdrop-blur-sm"
    }`;
    div.style.animationDelay = `${messageCount * 0.1}s`;
    // Convert line breaks and links
    div.innerHTML = text
        .replace(/\n/g, "<br>")
        .replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" class="underline hover:text-pink-300">$1</a>'
        );
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Show typing indicator
function showTyping() {
    if (!document.getElementById("typing")) {
        const typing = document.createElement("div");
        typing.id = "typing";
        typing.className = "bg-white/20 text-white px-5 py-3 rounded-2xl mr-auto backdrop-blur-sm";
        typing.innerHTML = "Tushar is typing<span class='dots'>...</span>";
        container.appendChild(typing);
        container.scrollTop = container.scrollHeight;
    }
}

// Remove typing indicator
function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}

// Allow sending with Enter (but not Shift+Enter)
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.dispatchEvent(new Event("submit"));
    }
});
