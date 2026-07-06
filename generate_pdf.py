import os
import re
import html
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# ---------------------------------------------------------
# Numbered Canvas for Header, Footer & Page X of Y
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        if self._pageNumber == 1:
            # Suppress headers/footers on title page
            return
            
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#4B5563"))
        
        # Draw Header
        self.drawString(54, 750, "Scalable-C: Architecture & Source Code Documentation")
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)
        
        # Draw Footer
        self.line(54, 60, 612 - 54, 60)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 45, page_text)
        self.drawString(54, 45, "Scalable WebSocket Chat System Architecture")
        self.restoreState()

# Helper for horizontal lines
def make_hr(color=colors.HexColor('#E5E7EB'), thickness=1, space_after=15):
    t = Table([['']], colWidths=[504], rowHeights=[thickness])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return KeepTogether([t, Spacer(1, space_after)])

# Main PDF Generator
def generate_pdf():
    base_dir = "." if os.path.basename(os.getcwd()) == "scalable-c" else "scalable-c"

    
    # Read files with fallback
    def read_file_content(relative_path):
        full_path = os.path.join(base_dir, relative_path)
        if not os.path.exists(full_path):
            return f"// File {relative_path} not found."
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    # Read and sanitize code files (replacing credentials with placeholders)
    index_ts = read_file_content("apps/server/src/index.ts")
    
    socket_ts = read_file_content("apps/server/src/services/socket.ts")
    # Clean the upstash secrets for security/formatting in PDF
    socket_ts = socket_ts.replace(
        "password: 'gQAAAAAAAQdeAAIncDI5N2Q0MDk1MjlmY2I0MjUzOTc2ZDJiM2NhNmZhOWZlNXAyNjc0MjI'", 
        "password: '<UPSTASH_REDIS_PASSWORD>'"
    )
    socket_ts = socket_ts.replace(
        "host: 'caring-lacewing-67422.upstash.io'", 
        "host: '<UPSTASH_REDIS_HOST>'"
    )
    
    socket_provider = read_file_content("apps/web/context/SocketProvider.tsx")
    page_tsx = read_file_content("apps/web/app/page.tsx")

    pdf_filename = "scalable-c-project-details.pdf"
    
    # Setup document: Margins 54pt (0.75 inch)
    # letter is 612 x 792 pt. Printable width is 504 pt. Printable height is 684 pt.
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    story = []

    # Get sample styles and customize
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#4B5563'),
        alignment=TA_CENTER,
        spaceAfter=30
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=18,
        spaceAfter=12,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0D9488'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Bullet'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=5,
        leftIndent=15
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=0
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1E3A8A')
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=body_style,
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#4B5563')
    )

    # Helper for code blocks
    def make_code_block(code_text, filename=None):
        lines = code_text.strip().split('\n')
        data = []
        
        if filename:
            header_style = ParagraphStyle(
                'FileHeader', 
                parent=body_style, 
                fontName='Helvetica-Bold', 
                fontSize=8.5, 
                textColor=colors.HexColor('#1E3A8A'), 
                spaceAfter=5
            )
            data.append([Paragraph(f"📄 {filename}", header_style)])
            
        for line in lines:
            indent = len(line) - len(line.lstrip())
            line_content = html.escape(line)
            # Maintain indentation via non-breaking spaces
            line_content = '&nbsp;' * indent + line_content.lstrip()
            data.append([Paragraph(line_content, code_style)])
            
        t = Table(data, colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('PADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,-1), (-1,-1), 6),
        ]))
        t.spaceAfter = 12
        if len(lines) < 25:
            return KeepTogether([t])
        return t


    # Helper for info callouts
    def make_callout(text, title="NOTE"):
        content = [
            Paragraph(f"<b>{title}:</b> {text}", ParagraphStyle('CalloutText', parent=body_style, fontSize=9.5, leading=14, textColor=colors.HexColor('#1E3A8A')))
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#BFDBFE')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('LINELEFT', (0,0), (-1,-1), 3.0, colors.HexColor('#2563EB')),
        ]))
        return KeepTogether([t, Spacer(1, 12)])

    # ---------------------------------------------------------
    # PAGE 1: TITLE PAGE
    # ---------------------------------------------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("SCALABLE-C", title_style))
    story.append(Paragraph("Production-Ready Horizontally Scalable WebSocket Chat System", subtitle_style))
    
    # Elegant divider
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=3, space_after=30))
    
    story.append(Spacer(1, 80))
    
    # Metadata Table
    meta_data = [
        [Paragraph("Project Name", meta_label_style), Paragraph("Scalable-C (WebSockets Monorepo)", meta_val_style)],
        [Paragraph("Primary Architectures", meta_label_style), Paragraph("Next.js, Socket.IO, Redis Pub/Sub, Turborepo", meta_val_style)],
        [Paragraph("Documentation Version", meta_label_style), Paragraph("v1.0.0 (Production Release)", meta_val_style)],
        [Paragraph("Author", meta_label_style), Paragraph("Karan Suthar", meta_val_style)],
        [Paragraph("Date Generated", meta_label_style), Paragraph("July 6, 2026", meta_val_style)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 354])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F3F4F6')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 2: TABLE OF CONTENTS
    # ---------------------------------------------------------
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    story.append(Spacer(1, 10))
    
    def make_toc_row(num, title, pagenum):
        return [
            Paragraph(f"<b>{num}</b>", body_style),
            Paragraph(title, body_style),
            Paragraph(f"Page {pagenum}", ParagraphStyle('TOCPage', parent=body_style, alignment=TA_RIGHT, fontName='Helvetica-Oblique', textColor=colors.HexColor('#4B5563')))
        ]
    
    toc_data = [
        make_toc_row("1", "Executive Summary & Architectural Problem Statement", 3),
        make_toc_row("2", "System Architecture & Redis Pub/Sub Synchronization", 4),
        make_toc_row("3", "Technology Stack Reference Table", 5),
        make_toc_row("4", "Monorepo Project Layout & File Structure", 6),
        make_toc_row("5", "Backend System Implementation Walkthrough (Node.js & ioredis)", 7),
        make_toc_row("6", "Frontend Context Provider & UI Implementation (Next.js)", 8),
        make_toc_row("7", "Setup, Configuration & Step-by-Step Installation Guide", 9),
        make_toc_row("8", "Conclusion & Production Scalability Roadmaps", 10)
    ]
    
    toc_table = Table(toc_data, colWidths=[30, 400, 74])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F3F4F6')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 3: EXECUTIVE SUMMARY & OVERVIEW
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary & Overview", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "Modern real-time applications rely on persistent WebSocket connections to deliver instant updates. "
        "However, as user traffic grows, a single WebSocket server instance becomes a bottleneck, capped by CPU, "
        "memory, and maximum file descriptors. Scaling WebSocket servers horizontally (adding more instances) "
        "introduces a critical synchronization problem: WebSockets are inherently <b>stateful</b>. "
        "A client establishes a persistent TCP link to one specific server instance. "
        "If Client A connects to <b>Server Instance 1</b> and Client B connects to <b>Server Instance 2</b>, "
        "they cannot communicate directly. When Client A sends a message, Server 1 receives it but does not "
        "know Client B exists, resulting in disconnected message silos.",
        body_style
    ))
    
    story.append(Paragraph(
        "<b>Scalable-C</b> solves this architectural challenge using a <b>Redis-backed Publish/Subscribe (Pub/Sub)</b> "
        "broker. Instead of servers trying to talk to each other directly or routing through a bottleneck database, "
        "every server instance connects to a shared, high-performance Redis channel. When a server instance "
        "receives an event from any local WebSocket client, it publishes the event to Redis. Every active server instance "
        "subscribes to that channel, receives the broadcast instantly, and distributes it to its own connected local clients. "
        "This decouples connections from event routing, allowing the server tier to scale out indefinitely.",
        body_style
    ))

    story.append(make_callout(
        "By utilizing serverless Upstash Redis, the network broker tier is kept fully serverless and highly performant. "
        "It supports instant message delivery across instances worldwide with minimal latency, avoiding the overhead of "
        "managing self-hosted Redis setups.",
        "Key Architectural Advantage"
    ))
    
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 4: SYSTEM ARCHITECTURE & DIAGRAM
    # ---------------------------------------------------------
    story.append(Paragraph("2. System Architecture & Message Flow", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "The diagram below demonstrates how Redis Pub/Sub bridges the communication gap between multiple decoupled server instances:",
        body_style
    ))
    
    # ASCII Architecture Diagram formatted inside a clean monospace block
    diag_text = (
        "             +------------------------------------------------+\n"
        "             |               Upstash Redis                    |\n"
        "             |               (Pub/Sub Broker)                 |\n"
        "             +-------^--------------------------------+-------+\n"
        "                     | Publish                        | Subscribe\n"
        "                     | (channel: \"messages\")          | (channel: \"messages\")\n"
        "                     |                                |\n"
        "        +------------+-------------+            +-----v-------------------+\n"
        "        |   Server Instance 1      |            |    Server Instance 2    |\n"
        "        |   (Node.js + Socket.IO)  |            |  (Node.js + Socket.IO)  |\n"
        "        +------------^-------------+            +-------------+-----------+\n"
        "                     |                                        |\n"
        "                     | WebSocket                              | WebSocket\n"
        "                     | Connection                             | Connection\n"
        "                     |                                        |\n"
        "            +--------+--------+                      +--------v--------+\n"
        "            |    Client A     |                      |    Client B     |\n"
        "            | (Next.js React) |                      | (Next.js React) |\n"
        "            +-----------------+                      +-----------------+"
    )
    story.append(make_code_block(diag_text))
    
    story.append(Paragraph("Detailed Step-by-Step Message Flow:", h2_style))
    story.append(Paragraph("1. <b>Client-to-Server Event:</b> Client A sends a chat message via WebSocket. The event is emitted as <code>'event:message'</code> and lands on Server Instance 1.", bullet_style))
    story.append(Paragraph("2. <b>Redis Publish:</b> Server Instance 1 parses the event and publishes the payload stringified as JSON to the Redis channel named <code>'messages'</code>.", bullet_style))
    story.append(Paragraph("3. <b>Redis Broadcast:</b> Redis distributes the payload to all server instances currently subscribed to the <code>'messages'</code> channel (Server 1 and Server 2).", bullet_style))
    story.append(Paragraph("4. <b>Local Socket Emit:</b> Upon receiving the message from Redis, Server Instance 2 emits the message locally using <code>io.emit('message')</code> to all of its connected WebSocket clients, including Client B.", bullet_style))
    story.append(Paragraph("5. <b>Client Render:</b> Client B's socket handler catches the incoming message and updates the local React state, presenting the message immediately in the chat interface.", bullet_style))
    
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 5: TECH STACK REFERENCE
    # ---------------------------------------------------------
    story.append(Paragraph("3. Technology Stack Reference", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "The following table highlights the technologies chosen, their specific roles in the project, "
        "and the engineering rationale behind them:",
        body_style
    ))
    
    tech_data = [
        [
            Paragraph("<b>Technology / Layer</b>", meta_label_style), 
            Paragraph("<b>General Use & Why It's Used</b>", meta_label_style), 
            Paragraph("<b>Specific Use In This Project</b>", meta_label_style)
        ],
        [
            Paragraph("<b>Next.js (React)</b><br/>Frontend Framework", body_style), 
            Paragraph("Next.js is an industry-standard React framework used generally for building highly optimized, SEO-friendly web applications. Developers choose it for its built-in routing, server-side rendering (SSR), and excellent developer experience.", body_style), 
            Paragraph("In this project, Next.js powers the client-side user interface (the <code>web</code> app). It serves the chat UI and manages the React state for incoming and outgoing messages while initializing the Socket.IO client.", body_style)
        ],
        [
            Paragraph("<b>Socket.IO</b><br/>Real-Time Engine", body_style), 
            Paragraph("Socket.IO is a widely-used library that enables low-latency, bidirectional, and event-based communication. It is preferred over raw WebSockets because it provides auto-reconnection, room management, and HTTP long-polling fallbacks.", body_style), 
            Paragraph("Used here on both frontend and backend to establish the persistent connection. It handles the actual transmission of chat messages (<code>'event:message'</code>) between the user's browser and the Node.js server.", body_style)
        ],
        [
            Paragraph("<b>Node.js & Express</b><br/>Backend Framework", body_style), 
            Paragraph("Node.js is a JavaScript runtime ideal for I/O-intensive tasks. Express is a minimalist web framework for Node.js. They are used together to quickly build scalable network applications and REST APIs.", body_style), 
            Paragraph("Serves as the foundation for the <code>server</code> app. Express sets up the HTTP server, which is then hijacked by Socket.IO to upgrade incoming connections to WebSockets. It also manages connections to Upstash Redis.", body_style)
        ],
        [
            Paragraph("<b>Upstash Redis</b><br/>Pub/Sub Engine", body_style), 
            Paragraph("Redis is an in-memory data structure store, used generally as a database, cache, and message broker. Upstash provides a serverless Redis offering that auto-scales and bills per request, eliminating infrastructure management.", body_style), 
            Paragraph("Acts as the critical message broker that enables horizontal scaling. When a message hits one server, it publishes to Upstash Redis, which instantly broadcasts it to all other connected server instances.", body_style)
        ],
        [
            Paragraph("<b>Turborepo</b><br/>Monorepo Tool", body_style), 
            Paragraph("Turborepo is a high-performance build system for JavaScript/TypeScript codebases. It is used generally to manage complex 'monorepos' (multiple projects in one repository) by caching build outputs and running scripts in parallel.", body_style), 
            Paragraph("Orchestrates the entire repository. It allows a single <code>yarn dev</code> command to simultaneously start the Next.js frontend and Node.js backend, and shares configurations (like ESLint and TypeScript) seamlessly between them.", body_style)
        ],
        [
            Paragraph("<b>TypeScript</b><br/>Language", body_style), 
            Paragraph("TypeScript is a strongly typed superset of JavaScript. It is used to catch errors at compile-time rather than run-time, significantly improving code quality, developer tooling, and maintainability in large codebases.", body_style), 
            Paragraph("Provides end-to-end type safety. By using TypeScript across both the <code>web</code> and <code>server</code> apps, we ensure that data structures (like the message payloads sent over WebSockets) remain strictly consistent across the network boundary.", body_style)
        ]
    ]
    
    tech_table = Table(tech_data, colWidths=[104, 200, 200])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tech_table)
    
    story.append(Spacer(1, 15))
    story.append(make_callout(
        "The monorepo structure makes sharing configurations (such as TypeScript, ESLint, and shared React components) "
        "extremely simple. It enables a clean separation of concerns while keeping both frontend and backend within a single git history.",
        "Monorepo Rationale"
    ))
    
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 6: DIRECTORY STRUCTURE
    # ---------------------------------------------------------
    story.append(Paragraph("4. Monorepo Project Layout & File Structure", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "Below is a structural tree of the Turborepo workspace. It shows the division of work into apps and package utilities:",
        body_style
    ))
    
    tree_text = (
        "scalable-c/\n"
        "├── apps/\n"
        "│   ├── web/                     # Next.js Frontend Client\n"
        "│   │   ├── app/\n"
        "│   │   │   ├── layout.tsx       # Main HTML root template & font loading\n"
        "│   │   │   ├── globals.css      # Core global resets\n"
        "│   │   │   └── page.tsx         # Chat UI page component with inputs & logs\n"
        "│   │   ├── context/\n"
        "│   │   │   └── SocketProvider.tsx # Client WebSocket manager context provider\n"
        "│   │   └── package.json\n"
        "│   └── server/                  # Node.js Server Backend\n"
        "│       ├── src/\n"
        "│       │   ├── index.ts         # Server entry point initializes socket & server\n"
        "│       │   └── services/\n"
        "│       │       └── socket.ts    # Socket.IO & Redis pub/sub broker bindings\n"
        "│       └── package.json\n"
        "├── packages/                    # Shared workspace utility modules\n"
        "│   ├── ui/                      # Shared global UI design components\n"
        "│   ├── eslint-config/           # Centralized lint rules\n"
        "│   └── typescript-config/       # Centralized strict config for compiler\n"
        "├── turbo.json                   # Build pipelines orchestrator\n"
        "└── package.json                 # Monorepo workspaces root config"
    )
    story.append(make_code_block(tree_text))
    
    story.append(Paragraph("Configuration Files Breakdown:", h2_style))
    story.append(Paragraph("• <b>turbo.json</b>: Defines cache rules for dev, build, lint, and type-check steps. If package source code hasn't changed, Turborepo will retrieve cached builds, saving developers hours of rebuild time.", bullet_style))
    story.append(Paragraph("• <b>package.json (Root)</b>: Configures workspaces array. Next.js and backend apps can install shared configurations using standard workspace aliases like <code>'packages/*'</code>.", bullet_style))
    story.append(Paragraph("• <b>packages/typescript-config</b>: Standardizes compiler configuration to ensure rigorous check constraints are unified between front and back-ends.", bullet_style))
    
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 7: BACKEND SYSTEM IMPLEMENTATION
    # ---------------------------------------------------------
    story.append(Paragraph("5. Backend Implementation Walkthrough", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "The backend starts a HTTP server and connects to the Upstash Redis cluster. "
        "It maintains separate Redis connections for Publishing and Subscribing, which is a required specification in Redis architecture.",
        body_style
    ))
    
    story.append(make_code_block(index_ts, "apps/server/src/index.ts"))
    story.append(make_code_block(socket_ts, "apps/server/src/services/socket.ts"))
    
    story.append(Paragraph("Backend Architectural Analysis:", h2_style))
    story.append(Paragraph("• <b>Dual Redis Client Pattern:</b> Redis connection handles blocking subscription command. A separate publishing client is required to broadcast outgoing messages. We instantiate two distinct clients: <code>pub</code> and <code>sub</code>.", bullet_style))
    story.append(Paragraph("• <b>Event Mapping:</b> We map incoming WS events (<code>event:message</code>) to out-bound Redis publications. When Redis receives it, it triggers the callback <code>sub.on('message')</code> which instantly calls <code>io.emit('message')</code> to push it to the frontend client.", bullet_style))
    story.append(Paragraph("• <b>CORS Configuration:</b> Set to allow all origins and headers, eliminating cross-origin errors commonly faced when starting frontend/backend on separate local ports (3000 vs 8000).", bullet_style))

    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 8: FRONTEND CLIENT IMPLEMENTATION
    # ---------------------------------------------------------
    story.append(Paragraph("6. Frontend Client Walkthrough", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "The React application wraps user routes inside a <code>SocketProvider</code> context. "
        "This context establishes a single persistent connection to the server when the client is loaded, "
        "and handles the local list of incoming and outgoing chat logs.",
        body_style
    ))
    
    story.append(make_code_block(socket_provider, "apps/web/context/SocketProvider.tsx"))
    story.append(make_code_block(page_tsx, "apps/web/app/page.tsx"))
    
    story.append(Paragraph("Frontend Code Analysis:", h2_style))
    story.append(Paragraph("• <b>State Management and Instability Protection:</b> When sending a message, the client appends it immediately locally as <code>'sent'</code> to ensure instant user-feedback. Since the server broadcasts the event back to everyone, we use a filtering mechanism in the <code>onMessageRecieved</code> handler to prevent duplicates.", bullet_style))
    story.append(Paragraph("• <b>Context Cleanups:</b> The <code>useEffect</code> block hooks into the component lifecycle to disconnect the socket and unbind listeners upon unmounting, preventing memory leaks.", bullet_style))

    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 9: SETUP, CONFIGURATION & DEV GUIDE
    # ---------------------------------------------------------
    story.append(Paragraph("7. Setup & Installation Guide", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph("Follow these steps to run the monorepo in a local environment:", body_style))
    
    story.append(Paragraph("1. Install Dependencies", h2_style))
    story.append(Paragraph("Run the root yarn installation command to setup packages for all sub-apps concurrently:", body_style))
    story.append(make_code_block("$ yarn install"))
    
    story.append(Paragraph("2. Configure Environment Variables", h2_style))
    story.append(Paragraph(
        "Create a file named <code>.env</code> in the <code>apps/server/</code> directory. "
        "Populate it with Upstash Redis credentials, using secure transport protocols (TLS):", 
        body_style
    ))
    env_content = (
        "UPSTASH_REDIS_URL=your_upstash_redis_url\n"
        "UPSTASH_REDIS_TOKEN=your_upstash_redis_token\n"
        "PORT=8080"
    )
    story.append(make_code_block(env_content, "apps/server/.env"))
    
    story.append(Paragraph("3. Run the Development Server", h2_style))
    story.append(Paragraph(
        "Execute the Turborepo dev runner. This launches both apps simultaneously. "
        "Turborepo routes and labels output lines according to their source project logs:", 
        body_style
    ))
    story.append(make_code_block("$ yarn dev"))
    
    story.append(Paragraph("The local development urls will resolve to:", body_style))
    urls_data = [
        [Paragraph("<b>Component</b>", meta_label_style), Paragraph("<b>Address</b>", meta_label_style)],
        [Paragraph("Next.js Client (UI)", body_style), Paragraph("http://localhost:3000", body_style)],
        [Paragraph("WebSocket Backend Server", body_style), Paragraph("http://localhost:8000 (Socket.IO)", body_style)]
    ]
    urls_table = Table(urls_data, colWidths=[200, 304])
    urls_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(urls_table)

    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 10: PRODUCTION GUIDELINES & CONCLUSION
    # ---------------------------------------------------------
    story.append(Paragraph("8. Conclusion & Production Scalability Roadmaps", h1_style))
    story.append(make_hr(colors.HexColor('#1E3A8A'), thickness=1.5, space_after=15))
    
    story.append(Paragraph(
        "This project establishes a solid foundation for building scaling real-time message routers. "
        "However, to take this into high-load production environments, the following scalability strategies should be prioritized:",
        body_style
    ))
    
    story.append(Paragraph("1. Load Balancing and Sticky Sessions", h2_style))
    story.append(Paragraph(
        "When placing WebSocket instances behind a Load Balancer (like NGINX, AWS ALB, or Cloudflare), "
        "you must enable <b>Sticky Sessions</b> (session affinity). This is because the Socket.IO handshake requires "
        "the client to send subsequent HTTP polling requests to the same server before upgrading to a persistent "
        "WebSocket connection. Without session affinity, requests will route to random instances, causing handshake failures.",
        body_style
    ))
    
    story.append(Paragraph("2. Database Persistence & Offline Queueing", h2_style))
    story.append(Paragraph(
        "Currently, chat messages are transient — they only exist in memory and in the active stream of Redis. "
        "If a user is offline, they miss the message entirely. In production, every incoming message should be persisted "
        "to a durable database (e.g. PostgreSQL, MongoDB, or Cassandra). Additionally, an offline notifications worker "
        "can check if a target user is offline, queuing push notifications or emails accordingly.",
        body_style
    ))

    story.append(Paragraph("3. Socket.IO Adapter optimization", h2_style))
    story.append(Paragraph(
        "While we implemented custom ioredis pub/sub logic, Socket.IO provides an official adapter (<code>@socket.io/redis-adapter</code>). "
        "For complex room management (e.g., separating users into distinct chatrooms like <code>'room-101'</code>), "
        "switching to the official Redis adapter is recommended. It handles room joining, leaving, and client queries "
        "across server boundaries automatically.",
        body_style
    ))
    
    story.append(Paragraph("4. Security Hardening", h2_style))
    story.append(Paragraph(
        "• <b>Authentication:</b> Wrap connections in authentication middleware (e.g., JWT verifying headers during the initial handshake).\n"
        "• <b>TLS/WSS:</b> Run connections over HTTPS and WSS to protect data in transit.\n"
        "• <b>Rate Limiting:</b> Implement connection rate limiters to prevent DDoS and spam on socket creation endpoints.",
        body_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {pdf_filename} with 10 pages.")

if __name__ == "__main__":
    generate_pdf()
