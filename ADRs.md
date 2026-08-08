# Architecture Decision Records — Advisor AI Fact Finder

Each record states the decision, why it was made, and — most importantly — **what would
break if it were reversed**. This last part is the point: these are the constraints a later
refactoring pass (by a different tool, model, or engineer with no shared context) must not
silently undo in the name of simplification.

If you hand this codebase to another model for refinement, hand it this file too.

---

## ADR-001 — Four immutable data layers

**Decision.** Maintain Transcript → AIExtraction → AdvisorReviewedData → FactFindContract as
four separate persisted layers. No layer overwrites another.

**Why.** Traceability is a core product requirement, not a feature: for any fact in a
submitted Fact Find, you must be able to answer what the AI extracted, why (evidence from
the transcript), and whether a human reviewed it.

**If reversed.** Collapsing layers (e.g. writing advisor edits over the AI extraction record)
destroys the audit trail. You could no longer prove what the AI originally produced versus
what the advisor corrected — which is exactly the evidence a compliance review would ask
for. This is the single most important constraint in the system.

**Watch for.** A refactoring pass that sees `originalAIValue` and `advisorValue` on the same
record and "simplifies" it to one field.

---

## ADR-002 — Human review as a mandatory, non-bypassable gate

**Decision.** No path exists from AI extraction to the official client record that doesn't
pass through explicit advisor accept/edit/reject. Default review status is `NEEDS_REVIEW`.

**Why.** Stated product rule: the AI must never write to the official client record without
representative review. Financial data with regulatory weight; an unreviewed AI value entering
a client record is a materially different product with materially different risk.

**If reversed.** Any "auto-accept above X confidence" shortcut converts this from a
human-in-the-loop system to an autonomous one. Confidence scores are model self-reports, not
calibrated probabilities — high confidence on a hallucinated value is a normal failure mode,
not an anomaly.

**Watch for.** Performance or UX optimizations that propose skipping review for
"high-confidence" fields. Reject them.

---

## ADR-003 — Pydantic validation between LLM output and everything downstream

**Decision.** All AI-generated structured data passes Pydantic validation before entering
application flow or persistence. Raw LLM JSON never reaches PostgreSQL.

**Why.** LLM output is untrusted input. Schema validation is the boundary that turns a
probabilistic text generator into a component with a contract.

**If reversed.** Malformed or hallucinated-shape responses propagate into the database and
surface as corrupted state later, far from the cause. Invalid AI responses are an expected,
handled error case — not an exception path.

---

## ADR-004 — Provider abstractions (LLMProvider, TranscriptionProvider) with mock implementations

**Decision.** Business logic depends on `LLMProvider` and `TranscriptionProvider` interfaces,
never on Ollama or faster-whisper directly. Mock implementations are first-class, selected by
env config (`LLM_PROVIDER`, `TRANSCRIPTION_PROVIDER`).

**Why.** Two reasons, both practical. (1) The full vertical slice must be runnable without
Ollama or faster-whisper installed — otherwise every developer needs a working local model
before they can touch the UI. (2) The MVP runs local models; production would likely use a
hosted provider. That swap should be config, not a rewrite.

**If reversed.** Coupling services to Ollama directly makes the app undevelopable without a
local model running, and turns the eventual hosted-provider migration into a refactor of
business logic rather than a config change.

---

## ADR-005 — FactFindMapper: AIExtraction is deliberately not FactFindContract

**Decision.** Keep the AI extraction schema and the canonical Fact Find contract as separate
models, joined by an explicit mapping service.

**Why.** They change for different reasons and on different cadences. The AI schema evolves
with the extraction approach (new fields, changed confidence model, different evidence
format). The Fact Find contract is closer to a system-of-record interface and changes with
downstream consumers.

**If reversed.** Merging them looks like removing a redundant layer, and immediately couples
prompt/extraction changes to the downstream contract — every extraction improvement becomes a
breaking schema change for consumers.

**Watch for.** "These two models are nearly identical, let's merge them" — that near-identity
is temporary and coincidental at MVP stage.

---

## ADR-006 — Deterministic speaker attribution before LLM extraction

**Decision.** Parse `Advisor:` / `Client:` labels in pasted transcripts into speaker-tagged
segments deterministically, before sending to the LLM. The LLM extracts from pre-tagged
segments rather than being asked to honor the labels itself.

**Why.** Advisor statements must not become client facts. In a labeled transcript, speaker
identity is a **factual, parseable answer** — not a judgment call. Asking the model to respect
labels introduces an avoidable failure mode: an advisor's suggestion ("a lot of clients your
age target around $2M") getting extracted as a client goal.

**If reversed.** You're relying on prompt adherence for a correctness property that has a
deterministic solution. This is the same principle applied elsewhere in the system: LLM output
is structured input to a deterministic step, not the final decision.

**Note.** This extends naturally to diarization later (pyannote.audio) — segments already
carry a speaker field, so the audio path plugs into the same structure.

---

## ADR-007 — Browser never communicates with the LLM runtime

**Decision.** React → FastAPI → LLMExtractionService → Ollama, always. No direct browser-to-
Ollama calls.

**Why.** Keeps prompts, client financial data, and model access behind the backend where
authorization, logging policy, and error handling apply.

**If reversed.** Exposes the model runtime to the client, bypasses backend authorization
checks, and puts client financial data into browser-originated requests to a service that has
no auth layer.

---

## ADR-008 — Append-only audit trail

**Decision.** `audit_events` is written, never updated or deleted. Events cover the full
lifecycle from `MEETING_CREATED` through `FACT_FIND_SUBMITTED`, including per-field
`FIELD_ACCEPTED` / `FIELD_EDITED` / `FIELD_REJECTED`.

**Why.** The audit trail is the evidence layer for the human-review guarantee in ADR-002.
An audit log that can be modified proves nothing.

**If reversed.** "Cleaning up" or deduplicating audit events removes the only record that the
review gate was actually honored.

---

## ADR-009 — Routes → Services → Repositories → SQLAlchemy

**Decision.** No database queries inside FastAPI route handlers. Services orchestrate;
repositories own data access.

**Why.** Standard separation, but load-bearing here specifically because the four-layer model
(ADR-001) has non-trivial write rules. Centralizing persistence in repositories is what keeps
"never overwrite a prior layer" enforceable in one place rather than scattered across routes.

---

## ADR-010 — Phase 6 (audio transcription) must not block phases 1–5

**Decision.** The paste-transcript path is the primary MVP workflow. faster-whisper audio
transcription lands last and is optional.

**Why.** Audio transcription adds a heavy dependency, a slow feedback loop, and a whole class
of failure modes — none of which are on the critical path for proving the core value
(conversation → extraction → review → fact find).

**If reversed.** Starting with audio means debugging Whisper installation and transcription
quality before you've validated whether the extraction-and-review experience is even right.

---

## Open questions to resolve during the build

- **Confidence display thresholds** (90+/70-89/<70) are presentational. Confirm they aren't
  used anywhere in logic — per ADR-002 they must not gate acceptance.
- **Evidence for derived values.** Some facts (e.g. total assets) may be computed rather than
  quoted. Decide whether these are extracted at all, or computed post-review from accepted
  facts — the latter is safer and keeps evidence meaningful.
- **Partial extraction failures.** If the LLM returns valid JSON for 8 of 10 categories,
  should the extraction be persisted as partial, or rejected wholesale? Partial with explicit
  per-category status is probably right, but decide before Phase 3.
