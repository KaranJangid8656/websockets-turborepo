'use client';
import { useState } from 'react';
import { useSocket } from '../context/SocketProvider';
import styles from './page.module.css';

export default function Page() {  
  const { sendMessage } = useSocket();
  const [message, setMessage] = useState('');
  
  // Local state for UI representation. We'll add local messages here when sent.
  // When socket listens are added in the Context, we can easily sync them!
  const [messages, setMessages] = useState<{text: string, type: 'sent' | 'received'}[]>([
    { text: "Welcome to the chatroom!", type: 'received' }
  ]);

  const handleSend = () => {
    if (message.trim()) {
      sendMessage(message);
      setMessages([...messages, { text: message, type: 'sent' }]);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatBox}>
        <div className={styles.header}>
          Real-time Global Chat
        </div>
        
        <div className={styles.messagesContainer}>
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`${styles.message} ${msg.type === 'sent' ? styles.sent : styles.received}`}
            >
              {msg.text}
            </div>
          ))}
        </div>
        
        <div className={styles.inputArea}>
          <input 
            type="text" 
            className={styles.chatInput}
            placeholder="Type a message..." 
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className={styles.sendButton} onClick={handleSend}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}