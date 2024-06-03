import React, {useState, useEffect} from 'react';
import './Threads.css'; // Import the CSS file

function Threads({setActiveThreadLookupId, fetchThreadMessages}) {  // Now receiving fetchThreadMessages via props
    const [threads, setThreads] = useState([]);

    // Fetch threads on component mount
    useEffect(() => {
        fetchThreads();
    }, []);

    const fetchThreads = async () => {
        const response = await fetch('http://127.0.0.1:5000/threads_get_all');
        const data = await response.json();
        setThreads(data);
    };

    const createNewThread = async () => {
        const response = await fetch('http://127.0.0.1:5000/thread_create', {method: 'POST'});
        const {lookup_id, thread_id} = await response.json();
        setActiveThreadLookupId(lookup_id);
        fetchThreads();
        fetchThreadMessages();  // Optionally refresh messages for new thread
    };

    return (
        <div>
            <div className="threads-header">
                <h2>
                    <a href="#"  onClick={createNewThread}>
                        + New Thread
                    </a>
                </h2>
            </div>
            <div className="thread-list">
                <ul>
                    {Object.entries(threads).reverse().map(([id, threadId]) => (
                        <li key={id}>
                            <a href="#" onClick={() => {
                                setActiveThreadLookupId(id);
                                fetchThreadMessages(); // Fetch messages when a thread is selected
                            }}  class="thread-item">
                                Thread #{id}
                            </a>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );



}

export default Threads;  // Ensure this line is present