document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const senseiCatElement = document.getElementById('sensei-cat-animation'); 
    const MAX_MESSAGES = 20;

    // Log if the cat element was found
    if (senseiCatElement) {
        console.log('Sensei Cat element found:', senseiCatElement);
    } else {
        console.error('Sensei Cat element NOT found! Stopping script.');
        return; // Stop if cat element is missing, as animations can't run
    }

    // Function to add a message to the chat history
    function addMessage(text, sender) {
        if (chatHistory.children.length >= MAX_MESSAGES) {
            chatHistory.removeChild(chatHistory.firstChild); // Remove the oldest message
        }

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        messageElement.textContent = text;
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to the bottom
    }

    // Function to trigger cat animations
    function triggerCatAnimation(animationName) {
        console.log(`Attempting to trigger animation: '${animationName}'`);
        if (!senseiCatElement) {
            console.error('Cannot trigger animation, Sensei Cat element is missing.');
            return;
        }

        if (senseiCatElement.animationTimeoutId) {
            clearTimeout(senseiCatElement.animationTimeoutId);
            senseiCatElement.animationTimeoutId = null;
        }

        // Updated list of specific animation classes for the image
        const specificAnimationClasses = ['animate-image-bounce', 'animate-image-tilt-zoom']; // Old: 'animate-yawn', 'animate-eye-narrowing', 'animate-yarn-batting'
        specificAnimationClasses.forEach(cls => senseiCatElement.classList.remove(cls));
        console.log('Removed existing specific image animation classes.');

        let classToAdd = null;
        if (animationName === 'yawn') {
            classToAdd = 'animate-image-bounce';
        } else if (animationName === 'eye_narrowing') {
            classToAdd = 'animate-image-tilt-zoom';
        }
        // Add other mappings here if new animation triggers are added

        if (classToAdd) {
            const animationDuration = getAnimationDuration(classToAdd);

            senseiCatElement.style.animation = 'none';
            console.log('Temporarily disabled default float animation.');
            void senseiCatElement.offsetWidth;

            senseiCatElement.classList.add(classToAdd);
            console.log(`Added animation class: ${classToAdd}`);

            senseiCatElement.animationTimeoutId = setTimeout(() => {
                senseiCatElement.classList.remove(classToAdd);
                senseiCatElement.style.animation = ''; 
                console.log(`Animation '${classToAdd}' finished. Restored default float animation.`);
                senseiCatElement.animationTimeoutId = null;
            }, animationDuration);
        } else {
            senseiCatElement.style.animation = '';
            console.log('No specific mapped animation for trigger or trigger was null. Ensuring default CSS float animation is active.');
        }
    }

    // Helper function to get animation durations (align with CSS)
    function getAnimationDuration(animationClassName) {
        switch (animationClassName) {
            case 'animate-image-bounce': // New class for yawn
                return 1000; // Matches CSS: animation: image-bounce-animation 1s ...
            case 'animate-image-tilt-zoom': // New class for eye-narrowing
                return 1500; // Matches CSS: animation: image-tilt-zoom-animation 1.5s ...
            // Add other animation durations here
            default:
                console.warn(`Unknown animation class for duration: ${animationClassName}`);
                return 0;
        }
    }

    // Function to send a message to the backend
    async function sendMessageToBackend(message) {
        try {
            addMessage(message, 'user'); // Add user message immediately
            userInput.value = ''; // Clear input field immediately

            const response = await fetch('http://localhost:8000/chat', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: "Unknown error occurred" }));
                console.error('Error from backend:', response.status, errorData);
                addMessage(`Sensei Whiskers is napping. Error: ${errorData.detail || response.statusText}`, 'bot');
                return;
            }

            const data = await response.json();
            addMessage(data.reply, 'bot'); // Changed data.response to data.reply
            console.log('Received from backend:', data); // Log the full backend response

            // Handle animation trigger from backend
            if (data.animation_trigger) {
                console.log(`Animation trigger received from backend: '${data.animation_trigger}'`);
                triggerCatAnimation(data.animation_trigger);
            } else {
                console.log('No animation_trigger field received from backend or it was null/empty.');
                // Ensure any specific animation is cleared if no trigger is sent
                triggerCatAnimation(null); 
            }

        } catch (error) {
            console.error('Failed to send message or parse response:', error);
            addMessage('Sensei Whiskers seems to be offline. Check the console for errors.', 'bot');
        }
    }

    // Event listener for the send button
    sendButton.addEventListener('click', () => {
        const messageText = userInput.value.trim();
        if (messageText) {
            sendMessageToBackend(messageText);
        }
    });

    // Event listener for pressing Enter in the input field
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendButton.click(); // This will trigger the click listener which calls sendMessageToBackend
        }
    });

    // Initial greeting from Sensei Whiskers (optional)
    // addMessage("Sensei Whiskers awaits your foolish questions...", 'bot');
    // triggerCatAnimation("float"); // Initial floating animation if we make it class-based
});
