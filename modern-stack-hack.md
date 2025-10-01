## Description

**Flowzmith** is an AI-powered smart contract generation and deployment platform specifically designed for the Flow blockchain ecosystem (for now; we plan to expand to all major blockchain networks like BNB, APTOS, ETH, SUI, etc.). It combines the power of LLMs with Flow's Cadence programming language to democratize smart contract development through natural language processing and automated deployment workflows and smart contract auditing/testing.

## Problem We're Solving

- **Complexity Barrier**: Smart contract development requires deep technical expertise in blockchain-specific languages like Cadence, creating barriers for developers and businesses
- **Time-Intensive Development**: Traditional smart contract creation involves lengthy development cycles, testing, and deployment processes
- **Documentation Fragmentation**: Flow/Cadence documentation is scattered across multiple sources, making it difficult for developers to find relevant information quickly
- **Deployment Complexity**: Setting up Flow projects, managing accounts, keys, and deployment configurations is complex for newcomers
- **Learning Curve**: New developers struggle to understand Cadence's resource-oriented programming model and Flow's unique architecture

## How the App Works

### **Multi-Modal Input Processing**
```
Natural Language → AI Processing → Cadence Smart Contract
File Upload (.cdc/.sol) → Conversion → Optimized Contract
Template Selection → Customization → Production-Ready Code
```

### **AI-Powered Generation Pipeline**
1. **LLM Processing**: Uses OpenAI GPT-4.1 or Groq models with specialized Cadence prompts
2. **Code Generation**: Generates complete Cadence contracts with proper resource handling
3. **Validation**: Validates generated code against Flow CLI standards
4. **Optimization**: Applies best practices and security patterns

### **Automated Deployment Workflow**
```bash
# CLI Workflow
python cli.py
→ Contract Creation → Flow Project Setup → Account Configuration → Deployment → Verification → Contract Audit & Testing Contract
```

### **Real-Time Monitoring**
- WebSocket connections for live deployment progress
- Real-time error handling and feedback
- Learning system that improves from deployment logs

## Notable Features

### **Core Features**
- **Multi-Modal Input**: Natural language, file uploads (.cdc/.sol), direct code input, templates
- **AI-Powered Generation**: Context-aware contract generation using Flow documentation
- **Flow Integration**: Seamless Flow CLI integration with automated project setup
- **Real-Time Learning**: Captures deployment logs to improve future generations
- **Documentation Intelligence**: Vector-powered semantic search through Cadence docs

### **Advanced Capabilities**
- **IPFS Storage**: Decentralized contract storage via Pinata integration
- **MCP Server Generation**: Automatic Model Context Protocol server creation; a new MCP server gets generated for every smart contract deployed on-chain.
- **Flow Automation**: Complete project scaffolding with accounts, keys, and configurations
- **WebSocket Updates**: Real-time progress tracking and notifications
- **GDPR Compliance**: User data controls, export, and deletion capabilities

### **Interfaces Developed**
- **Web Application**: Complete Next.js frontend with modern UI (WIP)
- **CLI Tool**: Comprehensive command-line interface with guided wizards
- **REST API**: Full-featured API with JWT authentication
- **WebSocket API**: Real-time communication for live updates

## Why Did We Build This

### **Our Mission**
To democratize Web3/blockchain development by making smart contract creation accessible to developers of all skill levels, from beginners to experts. Especially to existing Web2 developers looking to move onto a Web3 product.

### **Our Vision**
- **Lower Barriers**: Enable non-blockchain developers to create Flow smart contracts using natural language
- **Accelerate Development**: Reduce contract development time from days or hours to minutes.
- **Improve Quality**: Generate contracts following Flow best practices and security patterns
- **Foster Adoption**: Make blockchain more accessible to the broader developer community.
- **Educational Tool**: Help developers learn Cadence through AI-generated examples and explanations

## Modern Stack Cohosts Included

### **AI & Machine Learning**
- **OpenAI GPT-4.1**: Primary LLM for contract generation
- **Convex**: For backend API + DB (Next.js integration)
- **Groq**: Alternative high-speed inference engine
- **LangChain**: LLM orchestration and prompt management
- **ChromaDB**: Vector database for documentation search
- **Sentence Transformers**: Semantic search capabilities

### **Blockchain & Web3**
- **Flow CLI**: Official Flow blockchain command-line interface
- **Cadence**: Flow's resource-oriented smart contract language
- **IPFS/Pinata**: Decentralized storage for contract code
- **Web3 Integration**: Wallet connections and blockchain interactions

## Tech Stack List

### **Backend (Python)**
```
# Core Framework
FastAPI >= 0.104.0          # Modern async web framework
Uvicorn                     # ASGI server
Pydantic >= 2.5.0          # Data validation

# Database & ORM
SQLAlchemy >= 2.0.23        # Modern ORM with async support
Alembic >= 1.13.0          # Database migrations
PostgreSQL/SQLite           # Primary/development databases

# AI & Vector Processing
OpenAI >= 1.3.0            # GPT-4 integration
Groq >= 0.4.0              # Alternative LLM provider
LangChain >= 0.1.0         # LLM orchestration
ChromaDB >= 0.4.0          # Vector database
Sentence-Transformers       # Embedding models

# Async & Background Processing
Celery == 5.3.4            # Distributed task queue
Redis == 5.0.1             # Message broker
WebSockets >= 11.0         # Real-time communication

# Security & Authentication
python-jose[cryptography]   # JWT token handling
passlib[bcrypt]            # Password hashing
```

### **Frontend (Next.js/TypeScript)**
```
{
  "framework": "Next.js 15",
  "language": "TypeScript",
  "ui": {
    "@radix-ui/*": "Modern accessible components",
    "tailwindcss": "Utility-first CSS framework",
    "shadcn/ui": "Beautiful component library"
  },
  "ai": {
    "@ai-sdk/openai": "OpenAI integration",
    "@ai-sdk/groq": "Groq integration",
    "@langchain/core": "LangChain TypeScript"
  },
  "web3": {
    "@reown/appkit": "Web3 wallet connections",
    "wagmi": "React hooks for Ethereum"
  },
  "editor": {
    "@monaco-editor/react": "VS Code-like code editor"
  }
}
```

### **Infrastructure & DevOps**
```
# Containerization
Docker & Docker Compose     # Container orchestration
Nginx                      # Reverse proxy & SSL

# Development Tools
pytest                     # Testing framework
black                      # Code formatting
mypy                       # Type checking
pre-commit                 # Git hooks

# Monitoring & Logging
structlog                  # Structured logging
Health checks              # Application monitoring
```

### **Blockchain & Storage**
```bash
# Flow Ecosystem
Flow CLI                   # Official Flow tooling
Cadence                    # Smart contract language

# Decentralized Storage
IPFS                       # Distributed file system
Pinata                     # IPFS pinning service
```

## Prize Category

**OpenAI** - This project extensively leverages OpenAI's GPT-4.1 model as the primary AI engine for:
- Natural language to Cadence smart contract generation
- Context-aware code optimization using Flow documentation
- Intelligent error handling and code suggestions
- Educational content generation for learning Cadence development

The integration with OpenAI's API is central to the platform's core functionality, making it an ideal candidate for the OpenAI prize category.

## Prize Category

### **Primary: OpenAI** 
This project extensively leverages OpenAI's GPT-4 model as the primary AI engine for:
- Natural language to Cadence smart contract generation
- Context-aware code optimization using Flow documentation
- Intelligent error handling and code suggestions
- Educational content generation for learning Cadence development

The integration with OpenAI's API is central to the platform's core functionality, making it an ideal candidate for the OpenAI prize category.

### **Secondary: Convex Integration**
Flowzmith has integrated **Convex** as the real-time backend platform to enhance the user experience with:

#### **Real-Time Synchronization**
```typescript
Convex integration for live contract collaboration → Real-time contract editing and collaboration → Live deployment status across all connected clients
```

#### **Enhanced Features with Convex**
- **Live Collaboration**: Multiple developers can work on the same smart contract simultaneously with real-time updates
- **Instant Deployment Notifications**: All team members receive immediate updates when contracts are deployed or fail
- **Synchronized Learning**: AI improvements and learning insights are instantly shared across all users
- **Real-time Documentation Search**: Live updates to documentation search results as new content is indexed
- **Collaborative Code Review**: Team members can review and comment on generated contracts in real-time

#### **Architecture Integration**
```
Convex functions for smart contract management → Integration with OpenAI for contract generation → Store in Convex with real-time updates → Trigger real-time notifications
```

#### **Real-Time Analytics Dashboard**
- **Live Deployment Metrics**: Real-time success rates, gas usage, and performance metrics
- **AI Performance Tracking**: Live monitoring of OpenAI API usage and generation quality
- **User Activity Streams**: Real-time feed of contract creations, deployments, and learning progress
- **System Health Monitoring**: Live status of Flow CLI, IPFS, and all integrated services

This double integration positions Flowzmith as a cutting-edge platform that combines the power of OpenAI's language models with Convex's real-time synchronization capabilities, creating an unparalleled collaborative smart contract development experience.

## Firecrawl Integration for Flowzmith

### **Problem Firecrawl Solves**

- **Documentation Fragmentation**: Flow ecosystem documentation is scattered across multiple websites, GitHub repositories, and community resources
- **Real-time Information Access**: Static documentation becomes outdated quickly in the fast-evolving blockchain space
- **Content Accessibility**: Many valuable resources are behind JavaScript-heavy pages or protected content that traditional scrapers can't access
- **Data Quality**: Inconsistent formatting and structure across different documentation sources
- **Scalability**: Manual documentation curation doesn't scale with the growing Flow ecosystem

### **How Firecrawl Works with Flowzmith**

Firecrawl will be integrated into Flowzmith's knowledge base system to provide:

1. **Intelligent Web Crawling**: Automatically discovers and extracts Flow-related documentation from official sources, community blogs, and GitHub repositories
2. **Real-time Updates**: Continuously monitors Flow ecosystem websites for documentation updates and new resources
3. **Smart Content Processing**: Uses AI-powered extraction to identify relevant code examples, tutorials, and best practices
4. **Structured Data Output**: Converts web content into structured formats that integrate seamlessly with Flowzmith's vector database

### **Notable Features for Flowzmith Integration**

#### **Core Capabilities**
- **96% Web Coverage**: Accesses JavaScript-heavy and protected pages that traditional scrapers miss
- **Sub-second Performance**: Delivers results in less than 1 second for real-time agent responses
- **Zero Configuration**: Handles proxies, rate limits, and content loading automatically
- **Interactive Scraping**: Can click, scroll, and interact with dynamic content before extraction

#### **AI-Optimized Features**
- **Smart Wait Technology**: Intelligently waits for content to load, ensuring complete data extraction
- **Selective Caching**: Optimizes performance while ensuring fresh content when needed
- **Stealth Mode**: Crawls without being blocked, mimicking real user behavior
- **Multiple Output Formats**: Provides markdown, JSON, and screenshot outputs for comprehensive data capture

### **Why Firecrawl for Flowzmith**

- **Enhanced Learning System**: Provides fresh, comprehensive documentation for AI training and context
- **Real-time Intelligence**: Keeps Flowzmith's knowledge base current with the latest Flow ecosystem developments
- **Improved User Experience**: Delivers more accurate and up-to-date responses to user queries
- **Scalable Growth**: Automatically discovers new Flow resources as the ecosystem expands
- **Quality Assurance**: Ensures reliable data extraction from complex, dynamic web content

### **Modern Stack Integration**

**Firecrawl enhances Flowzmith's existing stack:**
- **AI/ML Layer**: Feeds fresh data to ChromaDB and LangChain for improved context
- **Backend Services**: Integrates with FastAPI endpoints for real-time documentation APIs
- **Frontend Experience**: Powers live search and documentation discovery features
- **Data Pipeline**: Works with Celery for background crawling and Redis for caching

Integrating Firecrawl positions Flowzmith as a truly intelligent, always-current platform that leverages the best of web data extraction technology to serve the Flow development community with the most accurate and up-to-date information available.