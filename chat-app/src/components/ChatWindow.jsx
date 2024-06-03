import React, { useState, useEffect, useRef } from 'react';
import { MessageBox } from 'react-chat-elements';
import 'react-chat-elements/dist/main.css'; // Import chat elements style
import './ChatWindow.css'; // Assuming you move your CSS rules to an external file

function ChatWindow({ handleSendMessage, messages }) {
    const [messageText, setMessageText] = useState('');
    const messageListRef = useRef(null);  // Create a ref for the message list container

    // Scroll to the bottom every time messages update
    useEffect(() => {
        if (messageListRef.current) {
            const { scrollHeight, clientHeight } = messageListRef.current;
            messageListRef.current.scrollTo(0, scrollHeight - clientHeight);
        }
    }, [messages]);

    const localHandleSendMessage = () => {
        console.log("Send button clicked");
        if (messageText.trim() !== '') {
            handleSendMessage(messageText);
            setMessageText('');  // Clear the input after sending
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            localHandleSendMessage();
        }
    };

    return (
        <div className="chat-window">
            <div className="message-list" ref={messageListRef}>
                {messages.map((msg, index) => (
                    <MessageBox key={index} {...msg} />
                ))}
            </div>
            <div className="rce-container-input">
                <div className="rce-input-wrapper">
                    <input
                        type="text"
                        className="rce-input"
                        placeholder="Type a message..."
                        value={messageText}
                        onChange={e => setMessageText(e.target.value)}
                        onKeyPress={handleKeyPress}
                    />
                    <label className="rce-floating-label">Type a message...</label>
                </div>
                <div className="rce-input-buttons">
                    <button
                        className="rce-button"
                        onClick={localHandleSendMessage}
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ChatWindow;
