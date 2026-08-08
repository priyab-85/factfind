# Advisor AI Fact Finder — Architecture Diagrams

Mermaid views of the MVP architecture described in `ARCHITECTURE.md`.

---

## 1. System overview (layers + trust boundary)

```mermaid
flowchart TB
    subgraph Browser["Browser — Financial Representative"]
        direction TB
        UI["React SPA<br/>(Vite + TypeScript)"]
        Pages["Pages & Features<br/>Portal · Client 360 · Fact Find · Review"]
        Components["shadcn/ui + Tailwind CSS"]
        Forms["React Hook Form + Zod"]
        State["TanStack Query<br/>(server state)"]
        APIClient["Typed API Client<br/>(no scattered fetch calls)"]

        UI --> Pages
        UI --> Components
        UI --> Forms
        UI --> State
        State --> APIClient
    end

    APIClient -->|"REST / JSON"| Routes

    subgraph Backend["Backend — FastAPI"]
        direction TB
        Routes["API Routes<br/>/clients · /meetings · /fact-finds · /audit"]
        Services["Application Services<br/>Client · Meeting · Extraction · Mapper · Audit"]
        Validation["Pydantic Validation<br/>(all LLM output validated here)"]
        Repos["Repositories<br/>(SQLAlchemy + Alembic)"]

        Routes --> Services
        Services --> Validation
        Services --> Repos
    end

    subgraph Providers["Provider Abstractions"]
        direction LR
        LLM["LLMProvider<br/>Ollama · Mock"]
        STT["TranscriptionProvider<br/>faster-whisper · Mock"]
    end

    subgraph External["External Runtimes (backend only)"]
        Ollama["Ollama<br/>Qwen / Llama instruct"]
        Whisper["faster-whisper<br/>(Phase 6 — optional)"]
    end

    DB[("PostgreSQL<br/>Docker Compose")]

    Services --> LLM
    Services --> STT
    LLM --> Ollama
    STT --> Whisper
    Repos --> DB

    Browser -.->|"❌ never direct"| Ollama

    classDef frontend fill:#eef4fb,stroke:#b6cfe8,color:#1a1a1a
    classDef backend fill:#f6f6f4,stroke:#d8d8d4,color:#1a1a1a
    classDef trust fill:#fdf0e6,stroke:#e8b98f,color:#1a1a1a
    classDef storage fill:#eef6ee,stroke:#b8d4b8,color:#1a1a1a
    classDef blocked fill:#fdecea,stroke:#e57373,color:#1a1a1a,stroke-dasharray:5 5

    class Browser,UI,Pages,Components,Forms,State,APIClient frontend
    class Backend,Routes,Services,Validation,Repos backend
    class Providers,LLM,STT,External,Ollama,Whisper trust
    class DB storage
```

**Key rule:** React always calls FastAPI. The browser never talks to Ollama or faster-whisper directly.

---

## 2. Core workflow (vertical slice)

```mermaid
flowchart LR
    A["Client Search"] --> B["Meeting Transcript"]
    B --> C["AI Extraction"]
    C --> D["Human Review"]
    D --> E["Fact Find Contract"]
    E --> F["Save + Audit"]

    classDef step fill:#eef4fb,stroke:#b6cfe8,color:#1a1a1a
    class A,B,C,D,E,F step
```

---

## 3. Four data layers (immutable pipeline)

Each layer is preserved. **No layer overwrites another.**

```mermaid
flowchart LR
    L1["Layer 1<br/>Raw Transcript<br/><i>immutable</i>"]
    L2["Layer 2<br/>AI Extraction<br/><i>evidence · confidence · speaker</i>"]
    L3["Layer 3<br/>Advisor Reviewed<br/><i>accept · edit · reject</i>"]
    L4["Layer 4<br/>FactFindContract<br/><i>canonical · validated</i>"]
    SOR[("System of Record<br/>PostgreSQL")]

    L1 --> L2 --> L3 --> L4 --> SOR

    classDef layer fill:#f6f6f4,stroke:#d8d8d4,color:#1a1a1a
    classDef gate fill:#fdf0e6,stroke:#e8b98f,color:#1a1a1a
    classDef record fill:#eef6ee,stroke:#b8d4b8,color:#1a1a1a

    class L1,L2 layer
    class L3 gate
    class L4,SOR record
```

When an advisor edits a value, both `originalAIValue` and `advisorValue` are kept for auditability.

---

## 4. AI extraction pipeline (trust gates)

```mermaid
flowchart TB
    Input["Transcript<br/>(paste or transcribed audio)"]
    Parse["Optional: parse Advisor/Client labels<br/>into speaker-tagged segments"]
    Extract["LLM Extraction Service<br/>(LLMProvider)"]
    JSON["Structured JSON"]
    Pydantic["Pydantic Validation"]
    Valid["Validated AIExtraction"]
    Review["Advisor Review UI<br/>default: NEEDS_REVIEW"]
    Mapper["FactFindMapper<br/>AI + advisor decisions"]
    Contract["FactFindContract"]
    Submit["Approve & Submit"]
    Persist[("PostgreSQL + audit_events")]

    Input --> Parse --> Extract --> JSON --> Pydantic
    Pydantic -->|"valid"| Valid
    Pydantic -->|"invalid"| Error["Handled error<br/>(no raw LLM JSON to DB)"]
    Valid --> Review
    Review -->|"accepted / edited only"| Mapper
    Mapper --> Contract --> Submit --> Persist

    classDef input fill:#eef4fb,stroke:#b6cfe8,color:#1a1a1a
    classDef process fill:#f6f6f4,stroke:#d8d8d4,color:#1a1a1a
    classDef gate fill:#fdf0e6,stroke:#e8b98f,color:#1a1a1a
    classDef store fill:#eef6ee,stroke:#b8d4b8,color:#1a1a1a
    classDef fail fill:#fdecea,stroke:#e57373,color:#1a1a1a

    class Input,Parse input
    class Extract,JSON,Pydantic,Valid,Mapper process
    class Review,Contract,Submit gate
    class Persist store
    class Error fail
```

---

## 5. Backend request flow (Routes → Services → Repositories)

```mermaid
sequenceDiagram
    autonumber
    actor Advisor as Financial Representative
    participant React as React SPA
    participant API as FastAPI Routes
    participant Svc as Application Services
    participant LLM as LLMProvider
    participant Val as Pydantic
    participant Repo as Repositories
    participant DB as PostgreSQL

    Advisor->>React: Paste transcript · Analyze Meeting
    React->>API: POST /api/meetings/{id}/extract
    API->>Svc: LLMExtractionService.extract()
    Svc->>LLM: extract_financial_facts(transcript)
    LLM-->>Svc: structured JSON
    Svc->>Val: validate AIExtraction
    Val-->>Svc: validated model
    Svc->>Repo: save ai_extractions
    Repo->>DB: INSERT
    DB-->>Repo: ok
    Repo-->>Svc: extraction id
    Svc-->>API: AIExtraction response
    API-->>React: facts + evidence + confidence
    React-->>Advisor: Review UI (Accept / Edit / Reject)

    Advisor->>React: Final review + attestation
    React->>API: POST /api/fact-finds
    API->>Svc: FactFindMapper + validate contract
    Svc->>Repo: save fact_finds + version + audit_events
    Repo->>DB: INSERT (append-only audit)
    DB-->>React: success
```

---

## 6. Persistence model (main tables)

```mermaid
erDiagram
    users ||--o{ meetings : creates
    clients ||--o{ meetings : has
    meetings ||--|| transcripts : contains
    meetings ||--o| ai_extractions : produces
    meetings ||--o| advisor_reviews : receives
    clients ||--o{ fact_finds : owns
    meetings ||--o| fact_finds : sources
    fact_finds ||--o{ fact_find_versions : versions
    fact_finds ||--o{ audit_events : audited
    meetings ||--o{ audit_events : audited

    users {
        string user_id PK
        string name
        string role
    }

    clients {
        string client_id PK
        string name
        string status
    }

    meetings {
        string meeting_id PK
        string client_id FK
        string advisor_id FK
        string status
    }

    transcripts {
        string transcript_id PK
        string meeting_id FK
        text raw_text
    }

    ai_extractions {
        string extraction_id PK
        string meeting_id FK
        json structured_data
    }

    advisor_reviews {
        string review_id PK
        string meeting_id FK
        json decisions
    }

    fact_finds {
        string fact_find_id PK
        string client_id FK
        string meeting_id FK
        json contract
    }

    fact_find_versions {
        string version_id PK
        string fact_find_id FK
        int version_number
    }

    audit_events {
        string event_id PK
        string event_type
        datetime timestamp
        json metadata
    }
```

---

## 7. Development modes (provider switching)

```mermaid
flowchart LR
    Env["Environment config"]
    Env --> LLMChoice{"LLM_PROVIDER"}
    Env --> STTChoice{"TRANSCRIPTION_PROVIDER"}

    LLMChoice -->|mock| MockLLM["MockLLMProvider<br/>full UI without Ollama"]
    LLMChoice -->|ollama| OllamaLLM["OllamaProvider<br/>Qwen / Llama"]

    STTChoice -->|mock| MockSTT["MockTranscriptionProvider"]
    STTChoice -->|faster_whisper| RealSTT["FasterWhisperProvider<br/>(Phase 6)"]

    classDef config fill:#eef4fb,stroke:#b6cfe8,color:#1a1a1a
    classDef mock fill:#f6f6f4,stroke:#d8d8d4,color:#1a1a1a
    classDef real fill:#eef6ee,stroke:#b8d4b8,color:#1a1a1a

    class Env,LLMChoice,STTChoice config
    class MockLLM,MockSTT mock
    class OllamaLLM,RealSTT real
```

Build against **mock providers first** (Phases 1–5). Wire Ollama in Phase 3 and faster-whisper in Phase 6 without blocking the transcript-based workflow.
