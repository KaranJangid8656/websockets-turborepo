'use client'; 
import React, { useCallback, useEffect, useContext, useState } from "react";
import { io, Socket } from "socket.io-client";

interface SocketProviderProps{
    children?: React.ReactNode;
}

interface ISocketContext{
    sendMessage: (msg: string) => void;
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

    const sendMessage: ISocketContext['sendMessage'] = useCallback((msg: string) => {
        console.log("Send Message", msg);
        if (socket) {
            socket.emit("event:message", { message: msg });
        }
    }, [socket])

    useEffect(()=>{
        const socket = io("http://localhost:8000");
        setSocket(socket);
        socket.on("connect", () => {
            console.log("Connected to server");
        });
        return () => {
            socket.disconnect();
            setSocket(null);
        };
    },[])
    return (
        <SocketContext.Provider value={{ sendMessage }}>
            {children}
        </SocketContext.Provider>
    )
}