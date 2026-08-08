# Advisor AI Fact Finder — Architecture

**Status:** MVP design, pre-build
**Source of requirements:** `MASTER_PROMPT.md`
**Core slice:** Client Search → Meeting Transcript → AI Extraction → Human Review → Fact Find Contract → Save

---

## 1. What this system actually is

Read plainly, this is not "an AI extraction app with some structure around it." It's a
**trust pipeline**. Almost every architectural decision below exists to enforce one
product rule:

> The AI must never write extracted information into the official client record without
> Financial Representative review.

Any change that weakens that boundary — however convenient — is a change to the product,
not just the implementation. That framing should govern the build and any later
refactoring pass (including by another tool or model).

---

## 2. Layered architecture

```
React SPA (Vite + TypeScript)
  pages/features · shadcn/ui + Tailwind · React Hook Form + Zod · TanStack Query
        ↓  (single typed API client layer — no scattered fetch calls)
REST / JSON
        ↓
FastAPI routes
  /api/clients · /api/meetings · /api/meetings/{id}/review · /api/fact-finds
        ↓  (routes contain no DB queries)
Application Services
  ClientService · MeetingService · LLMExtractionService · FactFindMapper · AuditService
        ↓
Provider abstractions + validation
  LLMProvider (Ollama | Mock) · TranscriptionProvider (faster-whisper | Mock)
  Pydantic validation ← every LLM output passes through here
        ↓
Repositories (SQLAlchemy, Alembic migrations)
        ↓
PostgreSQL (Docker Compose for local dev)
```

**Responsibility boundaries** (from the prompt, kept deliberately unmerged):
React = UX · React Hook Form = form state · Zod = frontend validation · TanStack Query =
server state · shadcn/Tailwind = components and styling · FastAPI = API and orchestration ·
faster-whisper = speech-to-text · Qwen/Llama = transcript understanding · Ollama = local LLM
runtime · Pydantic = backend and AI-output validation · SQLAlchemy = DB access ·
PostgreSQL = persistence.

---

## 3. The four data layers (the central constraint)

```
1. Raw Transcript      →  2. AI Extraction  →  3. Advisor Reviewed  →  4. FactFindContract
   immutable              + evidence,          accept/edit/reject      canonical, validated
                          confidence,                                   → System of Record
                          speaker, timestamps
```

**No layer ever overwrites another.** When an advisor edits a value, both are kept:

```json
{
  "field": "retirementAccounts[0].currentBalance",
  "originalAIValue": 450000,
  "advisorValue": 425000,
  "action": "EDITED",
  "reviewedBy": "...",
  "reviewedAt": "..."
}
```

This is what makes the three core traceability questions answerable for every fact:
**what did the AI extract, why (evidence), and has a human reviewed it?**

---

## 4. Trust boundary and guardrails

Three enforcement points, all non-negotiable:

1. **Pydantic validation** sits between LLM output and everything downstream. Raw LLM JSON
   never reaches PostgreSQL. Invalid AI responses are a handled error case, not a crash.
2. **Human review is a mandatory gate** between AI Extraction (layer 2) and Fact Find
   contract (layer 4). Default review status is `NEEDS_REVIEW` — nothing is implicitly
   approved. Confidence scores inform the advisor; they never auto-accept or auto-reject.
3. **The browser never talks to the LLM runtime.** React → FastAPI → LLMExtractionService →
   Ollama, always. This keeps AI processing, prompts, and client financial data behind the
   backend.

**Extraction rules the LLM must follow:** never invent values; never convert vague
statements into precise ones; never treat advisor recommendations, questions, hypotheticals,
or projections as client facts; preserve uncertainty (`approximate: true`); return `null`
when information is unavailable or wasn't discussed.

---

## 5. Known design risk — speaker attribution

The prompt correctly requires that advisor statements must not become client facts, and
defers diarization (pyannote.audio) past the MVP. But in the primary paste-transcript path,
the `Advisor:` / `Client:` labels are just text the LLM has to interpret and honor.

**Recommendation:** parse those speaker labels deterministically into speaker-tagged
segments *before* extraction, rather than trusting the model to respect them. Speaker
identity has a factual answer in a labeled transcript — look it up, don't infer it. The LLM
then receives pre-tagged segments and only needs to extract from client-attributed ones.

This mirrors the general principle used throughout: **LLM output is structured input to a
deterministic step, not the final decision.**

---

## 6. Provider abstractions — why the MVP is buildable

`LLMProvider` and `TranscriptionProvider` interfaces with mock implementations mean the
entire vertical slice runs without Ollama or faster-whisper installed:

```
LLM_PROVIDER=mock | ollama
TRANSCRIPTION_PROVIDER=mock | faster_whisper
```

Build against mocks first. Wire real Ollama in Phase 3. Otherwise you debug model output
and application logic simultaneously, which makes both harder.

Future providers (OpenAI, Azure OpenAI, Bedrock, vLLM) drop in behind the same interface —
business logic must not depend directly on Ollama.

---

## 7. Mapping layer

`AIExtraction` is deliberately **not** identical to `FactFindContract`. `FactFindMapper`
combines AI extraction + advisor decisions into the canonical contract.

This separation is intentional and worth defending under refactoring pressure: it lets the
AI schema evolve (new extraction fields, changed confidence model) independently of the
downstream fact-find schema, which is closer to a system-of-record contract and changes on
a different cadence for different reasons.

---

## 8. Persistence

Tables: `users`, `clients`, `meetings`, `transcripts`, `ai_extractions`, `advisor_reviews`,
`fact_finds`, `fact_find_versions`, `audit_events`.

`audit_events` is **append-only** — never updated, never deleted. Captured events include
`MEETING_CREATED`, `TRANSCRIPT_ADDED`, `AUDIO_TRANSCRIBED`, `AI_EXTRACTION_STARTED`,
`AI_EXTRACTION_COMPLETED`, `FIELD_ACCEPTED`, `FIELD_EDITED`, `FIELD_REJECTED`,
`FACT_FIND_REVIEWED`, `FACT_FIND_APPROVED`, `FACT_FIND_SUBMITTED`.

Access path: Routes → Services → Repositories → SQLAlchemy → PostgreSQL. No DB queries in
routes.

---

## 9. Build order

| Phase | Scope | Notes |
|---|---|---|
| 1 | React portal, client search, client profile, Fact Find workflow shell, mock APIs | Frontend proves the flow before any backend exists |
| 2 | FastAPI, PostgreSQL, SQLAlchemy, client + meeting APIs | Real persistence |
| 3 | Transcript submission, Ollama integration, extraction, Pydantic validation | First real AI path |
| 4 | Advisor Review UI — accept/edit/reject, evidence display, missing information | The most polished screen in the app |
| 5 | FactFindMapper, final review + attestation, submission, audit trail | Completes the slice |
| 6 | faster-whisper audio transcription | Optional — must never block phases 1–5 |

---

## 10. Definition of done

The MVP is complete when this runs end to end, locally, on synthetic data:

Search Michael Thompson → open profile → Start New Fact Find → paste sample transcript →
Analyze Meeting → FastAPI sends to configured LLM → structured extraction → Pydantic
validates → React displays facts with evidence and confidence → advisor accepts/edits/rejects
→ missing information identified → approved data mapped to `FactFindContract` → final review
→ attestation checked → submitted → PostgreSQL stores fact find + version → audit history
created → success page.

---

## 11. Explicitly out of scope

Trading · investment or product recommendations · portfolio optimization · suitability
determination · financial projections · account aggregation · Plaid · production SSO · CRM
integration · real-time streaming transcription · compliance surveillance · automatic plan
generation · automated client-record updates · native mobile · workflow engines · advanced
analytics.

The MVP proves **one** experience extremely well: Conversation → Extraction → Review →
Fact Find.

---

## 12. Security posture (MVP)

Synthetic client data only. Don't log raw transcripts or PII. Don't log LLM prompts
containing client financial data unless explicitly enabled for development against synthetic
data. Secrets in environment variables, never committed. Authorization checks on backend
endpoints. Mask highly sensitive values where appropriate. All AI processing stays behind the
backend.

Error handling must cover: LLM unavailable, invalid AI response, Pydantic validation failure,
transcription failure, database failure, API timeout, missing or empty transcript, fact find
validation errors. User-facing messages must be understandable; internal stack traces never
reach the frontend.
