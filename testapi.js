
const api_url = "http://127.0.0.1:8000";
const username = "testuser"

async function signup(username) {
    const response = await fetch(`${api_url}/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
    });

    if (response.ok) {
        const userId = await response.json();
        console.log('User ID:', userId);
        return userId;
    } else {
        throw new Error('Signup failed: ' + response.statusText);
    }
}
// signup(username) = Success
async function createChat(userId) {
    const response = await fetch(`${api_url}/chats/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
    });

    if (response.ok) {
        const chatId = await response.json();
        console.log('Chat ID:', chatId);
        return chatId;
    } else {
        throw new Error('Chat creation failed: ' + response.statusText);
    }
}
const user_id = "43f022db-0741-44e9-9bb1-a8df17c47f60"
// createChat(user_id)

async function createMessage(chatId, sender, content) {
    const response = await fetch(`${api_url}/messages/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_id: chatId, sender, content }),
    });

    if (response.ok) {
        const messageId = await response.json();
        console.log('Message ID:', messageId);
        return messageId;
    } else {
        throw new Error('Message creation failed: ' + response.statusText);
    }
}

const chat_id = "9df43e61-f6b8-4e65-8c73-0af755514199"
const sender = "USER"
const content = "yes, so i have this research i need to prepare for but i don't know where to start"
// createMessage(chat_id, sender, content) = Success

async function getChatMessages(chatId) {
    const response = await fetch(`${api_url}/chats/${chatId}/messages`);

    if (response.ok) {
        const messages = await response.json();
        console.log('Messages:', messages);
        return messages;
    } else {
        throw new Error('Failed to retrieve messages: ' + response.statusText);
    }
}

// getChatMessages(chat_id) = Success

async function getUserChats(userId) {
    const response = await fetch(`${api_url}/chats/${userId}`);

    if (response.ok) {
        const chatIds = await response.json();
        console.log('Chat IDs:', chatIds);
        return chatIds;
    } else {
        throw new Error('Failed to retrieve chats: ' + response.statusText);
    }
}

// getUserChats(user_id)