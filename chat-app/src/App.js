import React, { useState, useEffect } from 'react';
import SplitPane from 'react-split-pane';
import './App.css';
import 'react-chat-elements/dist/main.css'; // Import chat elements style

import ChatWindow from './components/ChatWindow';
import Threads from './components/Threads'; // Ensure you import the Threads component
import NodeGraph from './components/NodeGraph'; // Update path if necessary
import nodesData from './nodes.json'; // Update path if necessary

// const thread_lookup_id = '137'
// const assistant_id = 'asst_QgXDKXShLze0lqS6Spr4tVRU'
// Variables with initial values
let thread_lookup_id = '';
let assistant_id = '';

// Function to set the active thread lookup ID
function setActiveThreadLookupId(newLookupId) {
    thread_lookup_id = newLookupId;
    console.log(`Updated thread_lookup_id: ${thread_lookup_id}`);
}

// Function to set the active assistant ID
function setActiveAssistantId(newAssistantId) {
    assistant_id = newAssistantId;
    console.log(`Updated assistant_id: ${assistant_id}`);
}

const Sidebar = ({ position, content, isCollapsed, toggleSidebar }) => (
    <div className={`sidebar ${position} ${isCollapsed ? 'collapsed' : ''}`}>
        {position === 'left' && (
            <button className="toggle-button" onClick={toggleSidebar}>
                {isCollapsed ? '>' : '<'}
            </button>
        )}
        {!isCollapsed && (content || (position === "left" ? "" : "Right Sidebar"))}
    </div>
);

function App() {
    const [messages, setMessages] = useState([]);
    const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(false);

    const fetchThreadMessages = async () => {
        if (!thread_lookup_id) {
            console.log("No thread_lookup_id provided, skipping fetch.");
            return;
        }
        const response = await fetch(`http://127.0.0.1:5000/thread_messages_get?lookup_id=${thread_lookup_id}`);
        const data = await response.json();
        const formattedMessages = data.map(msg => ({
            position: msg.role.toLowerCase() === 'user' ? 'right' : 'left',
            type: 'text',
            text: msg.text,
            date: new Date(msg.date),
            sender: msg.role,
        }));
        setMessages(formattedMessages);
    };

    useEffect(() => {
        fetchThreadMessages();
    }, []);

    const handleSendMessage = async (customMessageText) => {
        console.log("handleSendMessage called with:", customMessageText);
        const textToSend = customMessageText.trim();
        if (textToSend) {
            const newMessage = {
                position: 'right',
                type: 'text',
                text: textToSend,
                date: new Date(),
                sender: 'user',
            };
            setMessages([...messages, newMessage]);

            try {
                const response = await fetch('http://127.0.0.1:5000/process_request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_input: textToSend,
                        assistant_id: assistant_id,
                        file_ids: ['file-aWJB3NOKHiJnfKgTyKrWgjo8'],
                        thread_lookup_id: thread_lookup_id,
                        llm_instructions: ''
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();

                setMessages([...messages, newMessage, {
                    position: result.role.toLowerCase() === 'assistant' || result.role.toLowerCase() === 'system' ? 'left' : 'right',
                    type: 'text',
                    text: result.response,
                    date: new Date(),
                    sender: result.role
                }]);

            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    };

    const toggleLeftSidebar = () => {
        setIsLeftSidebarCollapsed(!isLeftSidebarCollapsed);
    };

    return (
        <div className="App">
            <SplitPane split="vertical" minSize={50} defaultSize={isLeftSidebarCollapsed ? 50 : 200}>
                <Sidebar
                    position="left"
                    content={
                        <Threads
                            setActiveThreadLookupId={setActiveThreadLookupId}
                            fetchThreadMessages={fetchThreadMessages}
                        />
                    }
                    isCollapsed={isLeftSidebarCollapsed}
                    toggleSidebar={toggleLeftSidebar}
                />
                <SplitPane split="vertical" primary="second" minSize={100} defaultSize={200}>
                    <ChatWindow
                        handleSendMessage={handleSendMessage}
                        messages={messages}
                    />
                    <Sidebar
                        position="right"
                        content={
                            <NodeGraph nodesData={nodesData} />
                        }
                    />
                </SplitPane>
            </SplitPane>
        </div>
    );
}

export default App;
