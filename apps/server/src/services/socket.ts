import { Server } from "socket.io";
import { Redis } from "ioredis";

const pub = new Redis({
    host: 'caring-lacewing-67422.upstash.io',
    port: 6379,
    username: 'default',
    password: 'gQAAAAAAAQdeAAIncDI5N2Q0MDk1MjlmY2I0MjUzOTc2ZDJiM2NhNmZhOWZlNXAyNjc0MjI',
    tls: {} // REQUIRED for Upstash!
});

const sub = new Redis({
    host: 'caring-lacewing-67422.upstash.io',
    port: 6379,
    username: 'default',
    password: 'gQAAAAAAAQdeAAIncDI5N2Q0MDk1MjlmY2I0MjUzOTc2ZDJiM2NhNmZhOWZlNXAyNjc0MjI',
    tls: {} // REQUIRED for Upstash!
});

class SocketService {
    private _io: Server;

    constructor() {
        this._io = new Server({

            cors: {
                allowedHeaders: ["*"],
                origin: "*" // Fixed this CORS issue! It needs to be a single string for wildcard.
            }
        });
        sub.subscribe("messages");
    }

    public intListeners() {
        const io = this._io;
        console.log("Init Socket Listeners...");

        io.on("connect", (socket) => {
            console.log("User connected", socket.id);

            socket.on("event:message", async ({ message }: { message: string }) => {
                console.log("New Message received", message);
                await pub.publish("messages", JSON.stringify({ message }));
            })
        })
        sub.on("message", (channel, message) => {
            if (channel === "messages") {
                console.log("Message received from Redis", message);
                this._io.emit("message", message);

            }
        })
    }

    get io() {
        return this._io;
    }
}

export default SocketService;