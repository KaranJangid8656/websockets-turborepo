import {Server} from "socket.io";


class SocketService{
    private _io: Server ;

    constructor(){
        this._io = new Server();
    }   

    public intListeners() {
        const io = this._io;
        console.log("Init Socket Listeners...");

        io.on("connect", (socket) => {
            console.log("User connected", socket.id);

            socket.on("event:message", async ({ message }: {message: string}) => {
                console.log("New Message received", message);
            })
        })
    }
    
    get io(){
        return this._io;
    }

}

export default SocketService;