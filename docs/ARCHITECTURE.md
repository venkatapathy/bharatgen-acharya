# Architecture Overview

## 🏗️ Project Overview

**BharatGen Yojaka** is an intelligent, AI-powered learning platform designed to deliver interactive courses, personalized recommendations, and an AI chat assistant. It uses a hybrid architecture combining a traditional Django web application with a modern RAG (Retrieval-Augmented Generation) pipeline for AI features.

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|--------------|
| **Backend Framework** | **Django 4.2**, Django REST Framework (DRF) |
| **Database** | **SQLite** (default/dev), PostgreSQL (production ready) |
| **AI / LLM** | **Ollama** (Llama 3.1) for local inference |
| **Vector Database** | **ChromaDB** (local file-based) |
| **Embeddings** | **Sentence Transformers** (`all-MiniLM-L6-v2`) |
| **RAG Orchestration** | **LangChain** (integration logic) |
| **Frontend** | **Django Templates**, Vanilla JavaScript, Modern CSS (No SPA framework) |

---

## angle System Architecture

The system follows a modular **Monolithic** architecture where the AI components are integrated directly into the Django backend services.

```mermaid
graph TD
    Client[User / Browser]
    
    subgraph "Django Application Server"
        Router[URL Routing]
        
        subgraph "Apps Modules"
            Core[Core App\n(Auth/Users)]
            Learning[Learning App\n(Courses/Content)]
            Chat[Chat App\n(Session Logic)]
            Recs[Recommendation App]
        end
        
        subgraph "AI Services Layer (apps/rag)"
            RAG[RAG Pipeline]
            DocLoader[Document Loader]
            Embedder[Embedding Provider]
        end
    end

    subgraph "Data Storage"
        SQL[(SQLite / Postgres\nUser Data & Content)]
        VectorDB[(ChromaDB\nVector Embeddings)]
    end
    
    subgraph "External / Local AI"
        Ollama[Ollama Service\n(Llama 3.1 Model)]
    end

    %% Flow
    Client --> Router
    Router --> Core
    Router --> Learning
    Router --> Chat
    
    Chat --> RAG
    Recs --> Learning
    Recs --> SQL
    
    RAG --> VectorDB
    RAG --> Ollama
    RAG --> Embedder
    
    Learning --> SQL
    Core --> SQL
```

---

## 🧩 Key Components (Django Apps)

### 1. `apps/core`
*   **Responsibility:** Authentication, user profiles, and system-wide utilities.
*   **Key Models:** User profile extensions, base classes.

### 2. `apps/learning`
*   **Responsibility:** Manages the educational content structure.
*   **Key Models:** `LearningPath`, `Module`, `Lesson`, `UserProgress`.
*   **Logic:** Tracks what users have learned and serves course content.

### 3. `apps/chat`
*   **Responsibility:** Handles the user-facing chat interface and session management.
*   **Key Models:** `ChatSession`, `ChatMessage`.
*   **Flow:** Receives user input $\to$ Calls `apps/rag` $\to$ Saves history $\to$ Returns response.

### 4. `apps/rag` (The AI Brain)
*   **Responsibility:** Implements the RAG pipeline.
*   **Components:**
    *   `pipeline.py`: Orchestrates the retrieval and generation.
    *   `providers/`: Adapters for LLMs (Ollama) and Vector Stores (Chroma).
    *   `document_loader.py`: Ingests learning content into the vector store.

### 5. `apps/recommendations`
*   **Responsibility:** Suggests next steps or courses.
*   **Logic:** Analyzes `UserProgress` and content similarity to recommend new modules.

---

## 🔄 Data Flow: The RAG Pipeline

When a user asks a question in the chat:

1.  **Ingestion (Preprocessing):**
    *   Content from `apps/learning` is loaded.
    *   Text is chunked and converted to vectors using **Sentence Transformers**.
    *   Vectors are stored in **ChromaDB** (`data/chromadb/`).

2.  **Retrieval (Runtime):**
    *   User sends a message via API.
    *   The system embeds the query.
    *   **ChromaDB** finds the most relevant course content (context).

3.  **Generation:**
    *   The system constructs a prompt: `Context + User Question`.
    *   Prompt is sent to **Ollama (Llama 3.1)**.
    *   The LLM generates an answer based *only* on the provided course material.

## 📂 Directory Structure Highlights

*   `apps/`: Contains all business logic.
*   `data/`: Stores the local ChromaDB files and any static learning content files.
*   `templates/` & `static/`: Standard Django frontend assets.
*   `manage.py commands`:
    *   `build_rag_index`: Critical for keeping the AI "smart" about current content.
    *   `load_ai_content`: Seeds the database with initial learning paths.

