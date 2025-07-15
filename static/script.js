// Global variables
let conversationId = generateId();
let isTyping = false;

// Generate unique ID
function generateId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// DOM elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const typingIndicator = document.getElementById('typing-indicator');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    messageInput.focus();
});

// Handle Enter key
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isTyping) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTyping();
    
    try {
        // Send request to server
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Add bot response
            addBotMessage(data.response);
            conversationId = data.conversation_id;
        } else {
            addBotMessage('Sorry, I encountered an error. Please try again.');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addBotMessage('Sorry, I encountered an error. Please try again.');
    } finally {
        hideTyping();
        messageInput.focus();
    }
}

// Add user message
function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message user-message';
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
            <div class="message-time">Just now</div>
        </div>
        <div class="message-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
            </svg>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Add bot message
function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message bot-message';
    messageElement.innerHTML = `
        <div class="message-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V9C3 10.1 3.9 11 5 11H11V13H7V15H17V13H13V11H19C20.1 11 21 10.1 21 9Z"/>
            </svg>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
            <div class="message-time">Just now</div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Start new chat
async function startNewChat() {
    try {
        const response = await fetch('/new_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Clear chat messages
            chatMessages.innerHTML = '';
            
            // Add welcome message
            addBotMessage(data.response);
            
            // Update conversation ID
            conversationId = data.conversation_id;
            
            // Focus input
            messageInput.focus();
        }
        
    } catch (error) {
        console.error('Error starting new chat:', error);
    }
}

// Show typing indicator
function showTyping() {
    isTyping = true;
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

// Hide typing indicator
function hideTyping() {
    isTyping = false;
    typingIndicator.style.display = 'none';
}

// Scroll to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
