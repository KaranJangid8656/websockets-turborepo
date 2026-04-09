'use client';
import { useState } from 'react';
import { useSocket } from '../context/SocketProvider';
import styles from './page.module.css';

export default function Page() {  
  const { sendMessage, messages } = useSocket();
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      sendMessage(message);
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