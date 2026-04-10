<p align="center">
  <img src="https://res.cloudinary.com/dx9bvma03/image/upload/v1775738593/tr-removebg-preview_c1yat4.png" alt="Project Banner" width="400"/>
</p>

<p align="center">
  <img src="https://res.cloudinary.com/dx9bvma03/image/upload/v1775738871/websockets-removebg-preview_lvg9x7.png" alt="Socket.IO" height="130"/>
  &nbsp;&nbsp;&nbsp;
  
  <img src="https://res.cloudinary.com/dx9bvma03/image/upload/v1775738230/upstash-dark-bg_bopnp6.png" alt="Upstash" height="110"/>
  <img src="https://res.cloudinary.com/dx9bvma03/image/upload/v1775738049/redis_image-removebg-preview_asdmdd.png" alt="Redis" height="100"/>
  &nbsp;&nbsp;&nbsp;
</p>

<br>
<br>

<p align="center">
  A production-ready, horizontally scalable real-time chat application built with a modern monorepo architecture.
</p>

## 📖 About The Project

This is a **scalable, real-time chat application** designed to work seamlessly across multiple server instances. Traditional chat apps break when scaled horizontally — a user on Server A can't receive messages from a user on Server B. This project solves that problem using **Redis Pub/Sub** as a message broker to broadcast events across all connected server instances.

The app is built as a **Turborepo monorepo**, keeping the frontend (`web`) and backend (`server`) in a single, unified repository with shared tooling and configurations.

### ✨ Key Features 

- 🔴 **Real-time messaging** via WebSockets (Socket.IO)
- 📡 **Horizontally scalable** — multiple server instances stay in sync via Redis Pub/Sub
- 🌐 **Cross-server broadcasting** — messages sent to any server reach all connected clients
- 🎨 **Modern glassmorphism UI** built with Next.js
- 🚀 **Monorepo architecture** powered by Turborepo
- 🔒 **CORS-configured** for secure cross-origin WebSocket connections

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Next.js](https://nextjs.org/) (React framework) |
| **Backend** | [Node.js](https://nodejs.org/) + [Express](https://expressjs.com/) |
| **WebSockets** | [Socket.IO](https://socket.io/) |
| **Pub/Sub Broker** | [Upstash Redis](https://upstash.com/) (serverless Redis) |
| **Monorepo** | [Turborepo](https://turbo.build/) |
| **Language** | [TypeScript](https://www.typescriptlang.org/) (end-to-end) |
| **Package Manager** | [Yarn](https://yarnpkg.com/) |

---

## 🏗️ Project Structure

```
scalable-c/
├── apps/
│   ├── web/          # Next.js frontend (chat UI + Socket.IO client)
│   └── server/       # Node.js + Express backend (Socket.IO + Redis Pub/Sub)
├── packages/
│   ├── ui/           # Shared React component library
│   ├── eslint-config/ # Shared ESLint configuration
│   └── typescript-config/ # Shared TypeScript configuration
├── turbo.json        # Turborepo pipeline configuration
└── package.json      # Root workspace configuration
```

---

## ⚙️ How It Works

```
Client A (Browser)
      |
      | WebSocket (Socket.IO)
      ↓
   Server Instance 1  ──── Redis Pub/Sub ────  Server Instance 2
                                                      |
                                              WebSocket (Socket.IO)
                                                      ↓
                                              Client B (Browser)
```

1. A client sends a message via WebSocket to their connected server instance.
2. The server publishes the message to a **Redis channel**.
3. All other server instances are **subscribed** to that channel and receive the message.
4. Each server then **broadcasts** the message to its own connected clients.
5. Every user sees the message in real-time — regardless of which server they're connected to.

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- [Yarn](https://yarnpkg.com/)
- An [Upstash Redis](https://upstash.com/) account (free tier works)

### Installation

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd scalable-c
   ```

2. **Install dependencies**
   ```sh
   yarn install
   ```

3. **Configure environment variables**

   Create a `.env` file inside `apps/server/`:
   ```env
   UPSTASH_REDIS_URL=your_upstash_redis_url
   UPSTASH_REDIS_TOKEN=your_upstash_redis_token
   PORT=8080
   ```

4. **Run the development servers**
   ```sh
   yarn dev
   ```
   This starts both the Next.js frontend and the Node.js backend concurrently.

   | App | URL |
   |---|---|
   | Web (Frontend) | http://localhost:3000 |
   | Server (Backend) | http://localhost:8080 |

---

## 📦 Available Scripts

| Command | Description |
|---|---|
| `yarn dev` | Start all apps in development mode |
| `yarn build` | Build all apps for production |
| `yarn lint` | Lint all apps and packages |

---

## 🔗 Useful Links

- [Socket.IO Documentation](https://socket.io/docs/)
- [Upstash Redis](https://upstash.com/)
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [Next.js Documentation](https://nextjs.org/docs)
