'use client'; 
import React, { useCallback, useEffect, useContext, useState } from "react";
import { io, Socket } from "socket.io-client";

interface SocketProviderProps{
    children?: React.ReactNode;
}

interface ISocketContext{
    sendMessage: (msg: string) => void;
    messages: {text: string, type: 'sent' | 'received'}[];
}

const SocketContext = React.createContext<ISocketContext | null >(null);

export const useSocket = () => {
    const state = useContext(SocketContext);
    if(!state){
        throw new Error("state is undefined");
    }
    return state;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [messages, setMessages] = useState<{text: string, type: 'sent' | 'received'}[]>([
        { text: "Welcome to the global chatroom!", type: 'received' }
    ]);

    const sendMessage: ISocketContext['sendMessage'] = useCallback((msg: string) => {
        console.log("Send Message", msg);
        if (socket) {
            socket.emit("event:message", { message: msg });
            setMessages(prev => [...prev, { text: msg, type: 'sent' }]); // Show it instantly as sent
        }
    }, [socket])

    const onMessageRecieved = useCallback((msg: string) => {
        console.log("Message Recieved from Server", msg);
        try {
            const parsed = typeof msg === "string" ? JSON.parse(msg) : msg;
            const messageText = parsed.message;
            
            // To avoid double-showing messages we *just* sent (since the server broadcasts to EVERYONE), 
            // we'll filter it out if it already exists as the very last 'sent' message.
            setMessages(prev => {
                const lastMsg = prev.length > 0 ? prev[prev.length - 1] : undefined;
                if (lastMsg && lastMsg.text === messageText && lastMsg.type === 'sent') {
                    return prev; // We already showed this!
                }
                return [...prev, { text: messageText, type: 'received' }];
            });
        } catch (e) {
            console.error("Could not parse message", e);
        }
    }, [])

    useEffect(()=>{
        const socket = io("http://localhost:8000");
        socket.on("message", onMessageRecieved);
        setSocket(socket);
        socket.on("connect", () => {
            console.log("Connected to server");
        });
        return () => {
             socket.disconnect();
             socket.off("message", onMessageRecieved);
             setSocket(null);
        };
    }, [onMessageRecieved])

    return (
        <SocketContext.Provider value={{ sendMessage, messages }}>
            {children}
        </SocketContext.Provider>
    )
}