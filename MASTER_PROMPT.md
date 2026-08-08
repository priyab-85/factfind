# MASTER PROMPT — BUILD AN AI FINANCIAL FACT FINDER MVP

You are a senior full-stack engineer, AI engineer, UX designer, and financial-services application architect.

Build a working MVP called:

**Advisor AI Fact Finder**

The application helps a Financial Representative convert a client or prospect meeting into structured, reviewable Fact Find data.

The core workflow is:

**Client Search → Meeting Transcript → AI Extraction → Human Review → Fact Find Contract → Save**

The MVP must prioritize a working vertical slice over enterprise-scale complexity.

Do not over-engineer the solution.

---

# 1. PRIMARY USER

The primary user is a:

**Financial Representative / Financial Advisor**

The representative should be able to:

1. Log into a simulated Financial Representative Portal.
2. Search for an existing client or prospect.
3. Open the client profile.
4. Start a new Fact Find session.
5. Paste a meeting transcript.
6. Optionally upload a meeting recording.
7. Transcribe the audio when a recording is uploaded.
8. Analyze the transcript using an LLM.
9. Extract structured financial information.
10. Generate a meeting summary.
11. Identify missing information.
12. Review every AI-extracted fact.
13. Accept, edit, or reject extracted information.
14. Map approved information into the canonical Fact Find contract.
15. Perform a final review.
16. Approve and submit the Fact Find.
17. Save the completed Fact Find.
18. View an audit trail.

The AI must NEVER automatically write extracted information into the official client record without Financial Representative review.

---

# 2. MVP TECHNOLOGY STACK

Use the following technology stack.

Do not substitute frameworks unless explicitly requested.

## Frontend

Use:

* React.js
* TypeScript
* Vite

Build the frontend as a standalone Single Page Application.

Do NOT use Next.js.

---

## UI

Use:

* shadcn/ui
* Tailwind CSS

The interface should look like a modern enterprise financial-services application.

Use reusable components for:

* Buttons
* Cards
* Tables
* Tabs
* Dialogs
* Forms
* Inputs
* Selects
* Alerts
* Accordions
* Badges
* Progress indicators
* Toast notifications
* Confirmation dialogs

---

## Forms

Use:

**React Hook Form**

Use it for:

* Client forms
* Editing extracted facts
* Advisor review
* Final Fact Find review
* Approval and submission

---

## Frontend Validation

Use:

**Zod**

Use Zod for:

* Form validation
* API request validation
* Frontend Fact Find schemas

Frontend schemas should align with the backend Pydantic models.

---

## API / Server State

Use:

**TanStack Query**

Use it for:

* Client searches
* Client profile retrieval
* Meeting creation
* Transcript submission
* Starting AI analysis
* Loading extraction results
* Saving advisor review
* Loading Fact Finds
* Submitting Fact Finds
* Loading audit history

Do not scatter raw fetch calls throughout React components.

Create a reusable API client layer.

---

# 3. BACKEND

Use:

* Python
* FastAPI

The React frontend communicates with FastAPI using REST APIs.

Recommended endpoints:

GET /api/clients

GET /api/clients/{clientId}

POST /api/meetings

GET /api/meetings/{meetingId}

POST /api/meetings/{meetingId}/transcript

POST /api/meetings/{meetingId}/transcribe

POST /api/meetings/{meetingId}/extract

GET /api/meetings/{meetingId}/extraction

PUT /api/meetings/{meetingId}/review

POST /api/fact-finds

GET /api/fact-finds/{factFindId}

GET /api/fact-finds/{factFindId}/audit

---

# 4. DATABASE

Use:

**PostgreSQL**

For local development, run PostgreSQL using Docker Compose.

Create tables such as:

users

clients

meetings

transcripts

ai_extractions

advisor_reviews

fact_finds

fact_find_versions

audit_events

---

# 5. ORM

Use:

**SQLAlchemy**

Use:

**Alembic**

for database migrations.

Do not embed database queries directly inside FastAPI routes.

Use:

Routes

→

Services

→

Repositories

→

SQLAlchemy

→

PostgreSQL

Recommended backend structure:

backend/

app/

api/

models/

schemas/

repositories/

services/

ai/

transcription/

database/

core/

main.py

---

# 6. BACKEND VALIDATION

Use:

**Pydantic**

Pydantic should be the authoritative schema validation layer for backend application data.

All AI-generated structured data must pass through Pydantic validation.

Create Pydantic models for:

Client

Meeting

Transcript

AIExtraction

ExtractedFact

Income

Asset

RetirementAccount

Liability

InsurancePolicy

FinancialGoal

ClientPriority

MissingInformation

MeetingSummary

FollowUpAction

AdvisorReview

FactFindContract

AuditEvent

Never allow arbitrary LLM JSON to flow directly into the application database.

---

# 7. APPLICATION ARCHITECTURE

Use this architecture:

React.js

↓

React Hook Form

Zod

TanStack Query

shadcn/ui

Tailwind CSS

↓

REST API

↓

FastAPI

↓

Application Services

↓

AI / Transcription / Database Services

The backend connects to:

PostgreSQL

faster-whisper

Ollama

Qwen or Llama instruct model

Pydantic validation

---

# 8. MVP SCREEN 1 — PORTAL DASHBOARD

Create a simulated Financial Representative Portal.

Header:

**Advisor Portal**

Example logged-in representative:

Sarah Johnson

Financial Representative

Display dashboard cards:

* Clients
* Prospects
* Meetings Today
* Fact Finds Awaiting Review
* Completed Fact Finds
* Follow-Up Items

Create application tiles:

* Client Profile
* Fact Finder
* Financial Planning
* Insurance

Only Fact Finder must be fully functional.

---

# 9. CLIENT SEARCH

Create a prominent search field:

**Search clients and prospects**

Allow search by:

* Name
* Client ID
* Email

Create at least five fictional clients.

Example primary client:

Michael Thompson

Client ID:

C-100245

Status:

Client

Age:

52

Occupation:

Senior Engineering Manager

Location:

Charlotte, NC

Advisor:

Sarah Johnson

Selecting the client opens the Client 360 page.

---

# 10. CLIENT 360

Display:

## Personal Information

Name

Age

Occupation

Employer

Marital Status

Dependents

Contact information

---

## Financial Snapshot

Income

Assets

Retirement accounts

Liabilities

Insurance

Goals

Show a prominent button:

**Start New Fact Find**

---

# 11. FACT FIND WORKFLOW

Display a workflow stepper:

1. Client
2. Meeting
3. AI Analysis
4. Review
5. Fact Find
6. Submit

The user should always know which step they are on.

---

# 12. MEETING INPUT

Create a new Fact Find session.

Display:

Client

Advisor

Meeting Date

Meeting ID

Status

Provide two input options.

## Option A — Paste Transcript

Provide a large text area.

This should be the PRIMARY MVP workflow.

## Option B — Upload Recording

Allow:

MP3

WAV

M4A

Audio transcription can be implemented as the second phase of the MVP.

Provide:

**Analyze Meeting**

button.

---

# 13. TRANSCRIPTION

Use:

**faster-whisper**

Its responsibility is:

Meeting Audio

→

Text Transcript

Create an abstraction:

TranscriptionProvider

with:

transcribe(audio_file)

Implement:

FasterWhisperProvider

MockTranscriptionProvider

Do not couple application business logic directly to faster-whisper.

The provider should return transcript segments with timestamps whenever possible.

Example:

{
"speaker": null,
"startTime": 125.4,
"endTime": 131.8,
"text": "My 401k is around four hundred and twenty-five thousand dollars."
}

---

# 14. OPTIONAL SPEAKER DIARIZATION

Design the system so speaker diarization can later be added.

Potential technology:

**pyannote.audio**

Its responsibility would be identifying:

ADVISOR

CLIENT

OTHER

Do not make diarization mandatory for the initial MVP.

However, structure transcript segments so a speaker can be stored.

Speaker identification is important because advisor statements must not automatically become client facts.

---

# 15. LLM RUNTIME

Use:

**Ollama**

Ollama is responsible for running the selected LLM locally during MVP development.

React must NEVER communicate directly with Ollama.

Use:

React

→

FastAPI

→

LLMExtractionService

→

Ollama

Create an interface:

LLMProvider

with a method conceptually similar to:

extract_financial_facts(transcript, schema)

Implement:

OllamaProvider

Keep it possible to add:

OpenAIProvider

AzureOpenAIProvider

BedrockProvider

VLLMProvider

later.

Business logic must not depend directly on Ollama.

---

# 16. LLM MODEL

Use a capable instruction model supported by Ollama.

Prefer:

Qwen-class instruct model

or

Llama-class instruct model

Choose a model appropriate to the available hardware.

The LLM's job is:

Transcript

→

Structured Financial Information

The LLM should:

* Extract financial facts
* Extract financial goals
* Extract client priorities
* Generate meeting summaries
* Identify missing information
* Generate suggested follow-up questions
* Preserve evidence for extracted facts

---

# 17. AI EXTRACTION RULES

The AI MUST follow these rules.

Never invent financial information.

Never convert vague statements into unsupported precise values.

Never treat advisor recommendations as client facts.

Never treat questions as client facts.

Never treat hypothetical financial scenarios as actual client information.

Never treat projections as existing assets.

Preserve uncertainty.

When a value is approximate, record that it is approximate.

If information is unavailable:

return null.

If information was not discussed:

return null or an empty collection.

---

# 18. STRUCTURED EXTRACTION MODEL

AI extraction should produce structured JSON.

Every important financial value should contain metadata similar to:

{
"value": 425000,
"confidence": 0.94,
"evidence": "My 401k is around four hundred and twenty-five thousand dollars.",
"speaker": "CLIENT",
"startTime": 842.5,
"endTime": 847.2,
"approximate": true,
"reviewStatus": "NEEDS_REVIEW"
}

Evidence is mandatory whenever possible.

---

# 19. PERSONAL INFORMATION EXTRACTION

Extract:

fullName

dateOfBirth

age

address

email

phone

maritalStatus

spouseName

dependents

occupation

employer

Do not display sensitive data unnecessarily.

---

# 20. INCOME

Extract income sources.

Fields:

type

description

owner

annualAmount

Examples:

Salary

Bonus

Commission

Business Income

Rental Income

Investment Income

Other

---

# 21. ASSETS

Extract:

assetType

description

institution

owner

currentValue

Examples:

Checking

Savings

Brokerage

Real Estate

Business Ownership

Cash

Other

---

# 22. RETIREMENT ACCOUNTS

Extract:

accountType

institution

owner

currentBalance

annualContribution

employerMatch

beneficiary

Support:

401(k)

403(b)

Traditional IRA

Roth IRA

Pension

SEP IRA

SIMPLE IRA

Other

---

# 23. LIABILITIES

Extract:

liabilityType

institution

owner

currentBalance

monthlyPayment

interestRate

remainingTerm

Examples:

Mortgage

Credit Card

Auto Loan

Student Loan

Personal Loan

Business Loan

Other

---

# 24. INSURANCE

Extract:

insuranceType

carrier

owner

coverageAmount

premium

beneficiary

Support:

Term Life

Permanent Life

Disability

Long-Term Care

Other

---

# 25. FINANCIAL GOALS

Extract:

category

description

targetAmount

targetDate

targetAge

priority

Support priorities:

HIGH

MEDIUM

LOW

Examples:

Retirement

College Funding

Debt Reduction

Emergency Fund

Home Purchase

Estate Planning

Insurance Protection

Investment Growth

---

# 26. CLIENT PRIORITIES

Identify what matters most to the client.

Examples:

Retirement Readiness

Market Volatility

College Funding

Debt Reduction

Insurance Protection

Estate Planning

Investment Growth

Taxes

Healthcare Expenses

Return no more than five priorities.

Identify the top three when supported by the conversation.

---

# 27. MEETING SUMMARY

Generate:

meetingSummary

keyDiscussionPoints

clientConcerns

financialGoals

decisionsMade

openQuestions

followUpActions

Keep the summary factual.

Do not include information that cannot be supported by the transcript or authorized existing client data.

---

# 28. MISSING INFORMATION

Identify important Fact Find fields that were not discussed.

Example:

{
"field": "mortgage.interestRate",
"category": "Liabilities",
"reason": "Mortgage balance was discussed, but interest rate was not provided.",
"suggestedQuestion": "What interest rate are you currently paying on your mortgage?"
}

Display this information under:

**Suggested Follow-Up Questions**

The Financial Representative decides whether to use each question.

---

# 29. AI CONFIDENCE

Store confidence as:

0.0 – 1.0

Display:

90%-100%

High Confidence

70%-89%

Medium Confidence

Below 70%

Low Confidence

Do not treat confidence as mathematical certainty.

Never automatically reject or approve information solely because of the confidence score.

---

# 30. AI EXTRACTION PIPELINE

Implement:

Transcript

↓

LLM Extraction

↓

Structured JSON

↓

Pydantic Validation

↓

Validated AIExtraction

↓

Advisor Review

The LLM should never write directly to PostgreSQL Fact Find records.

---

# 31. HUMAN REVIEW SCREEN

Create the most polished screen in the application:

**Review AI Extracted Information**

Create tabs:

Summary

Personal

Income

Assets

Retirement

Liabilities

Insurance

Goals

Missing Information

For each extracted item display:

Field

AI Value

Confidence

Evidence

Speaker

Status

Provide actions:

Accept

Edit

Reject

Default:

NEEDS REVIEW

---

# 32. EDITING AI DATA

If the advisor edits a value:

Preserve:

originalAIValue

advisorValue

reviewAction

reviewedBy

reviewedAt

Example:

{
"field": "retirementAccounts[0].currentBalance",
"originalAIValue": 450000,
"advisorValue": 425000,
"action": "EDITED"
}

Never overwrite the original extraction.

---

# 33. FOUR DATA LAYERS

Maintain four separate logical data layers.

## Layer 1

Raw Transcript

## Layer 2

AI Extraction

## Layer 3

Advisor Reviewed Data

## Layer 4

Final Fact Find Contract

The flow must be:

Transcript

→

AIExtraction

→

AdvisorReviewedFactFind

→

FactFindContract

→

System of Record

Never overwrite one layer with another.

---

# 34. FACT FIND CONTRACT

Create a canonical FactFindContract.

Example:

{
"factFindId": "",
"clientId": "",
"advisorId": "",
"meetingId": "",
"createdAt": "",

"personalInformation": {},

"income": [],

"assets": [],

"retirementAccounts": [],

"liabilities": [],

"insurancePolicies": [],

"financialGoals": [],

"clientPriorities": [],

"meetingSummary": {},

"missingInformation": [],

"advisorReview": {
"reviewedBy": "",
"reviewedAt": "",
"approved": false
}
}

Create Pydantic models for this contract.

Create matching TypeScript/Zod definitions on the frontend.

---

# 35. MAPPING LAYER

Do not make AIExtraction identical to FactFindContract.

Create a mapping service:

FactFindMapper

Responsibilities:

AI Extraction

*

Advisor Decisions

↓

Canonical FactFindContract

This separation is intentional.

It allows the AI schema and downstream Fact Find schema to change independently.

---

# 36. FINAL REVIEW

Create a page:

**Final Fact Find Review**

Display:

Client Information

Income

Assets

Retirement Accounts

Liabilities

Insurance

Financial Goals

Client Priorities

Meeting Summary

Missing Information

Advisor Notes

Require an attestation checkbox:

"I have reviewed the information generated from this meeting and confirm that the information being submitted accurately reflects the client discussion to the best of my knowledge."

Provide:

Save Draft

Approve & Submit

Approve & Submit must be disabled until the attestation is checked.

---

# 37. SUBMIT FACT FIND

Create:

POST /api/fact-finds

Before saving:

Validate the final contract using Pydantic.

Then:

Save the Fact Find.

Create a Fact Find version.

Create an audit event.

Return a success response.

Display:

**Fact Find Successfully Saved**

Show:

Client

Fact Find ID

Advisor

Date

Status

Provide:

View Fact Find

Return to Client

---

# 38. AUDIT TRAIL

Create an append-only audit history.

Capture events such as:

MEETING_CREATED

TRANSCRIPT_ADDED

AUDIO_TRANSCRIBED

AI_EXTRACTION_STARTED

AI_EXTRACTION_COMPLETED

FIELD_ACCEPTED

FIELD_EDITED

FIELD_REJECTED

FACT_FIND_REVIEWED

FACT_FIND_APPROVED

FACT_FIND_SUBMITTED

Each event contains:

eventId

timestamp

userId

clientId

meetingId

factFindId

eventType

metadata

Never overwrite audit events.

---

# 39. SAMPLE CLIENT

Seed the application with synthetic data.

Primary sample client:

Michael Thompson

Client ID:

C-100245

Age:

52

Marital Status:

Married

Dependents:

2

Occupation:

Senior Engineering Manager

Annual Salary:

$185,000

Known Assets:

Savings:

$75,000

401(k):

$425,000

Brokerage:

$185,000

Primary Residence:

$850,000

Liabilities:

Mortgage:

$310,000

Auto Loan:

$22,000

Insurance:

Term Life Insurance:

$750,000

Goals:

Retire at age 62

Target retirement income:

$120,000 annually

Fund daughter's college

Potentially purchase vacation property

Concerns:

Market volatility

Retirement readiness

College expenses

---

# 40. SAMPLE MEETING TRANSCRIPT

Preload this fictional transcript.

Advisor:

Michael, what would you say is your biggest financial priority right now?

Client:

Definitely retirement. I'm 52 now and ideally I'd like to stop working around 62.

Advisor:

How much do you currently have saved for retirement?

Client:

My 401k is around $425,000. I also have an investment account with Fidelity that's about $185,000.

Advisor:

What about cash savings?

Client:

We keep roughly $75,000 in savings.

Advisor:

Any major debts?

Client:

Our mortgage has about $310,000 left. We also owe around $22,000 on my wife's car.

Advisor:

What would you like your retirement income to look like?

Client:

If we could have around $120,000 a year, I'd feel pretty comfortable.

Advisor:

Anything else you're concerned about?

Client:

The market makes me nervous. And our daughter starts college in three years, so I'm trying to figure out how to pay for that without hurting retirement.

---

# 41. EXPECTED EXTRACTION

The application should identify approximately:

401(k):

$425,000

Brokerage:

$185,000

Savings:

$75,000

Mortgage:

$310,000

Auto Loan:

$22,000

Retirement Target Age:

62

Target Retirement Income:

$120,000 annually

College Goal:

Daughter begins college in approximately three years

Primary Concerns:

Retirement Readiness

Market Volatility

College Funding

The system should preserve evidence from the transcript for these values.

---

# 42. SECURITY

Assume all client information is sensitive.

For the MVP:

Use synthetic client data only.

Do not log raw transcripts unnecessarily.

Do not log PII to console output.

Do not log LLM prompts containing client financial data unless explicitly enabled for development with synthetic data.

Store environment secrets in environment variables.

Do not commit secrets.

Implement authorization checks on backend endpoints.

Mask highly sensitive values when appropriate.

Keep AI processing behind the backend.

The browser must never directly call the LLM runtime.

---

# 43. ERROR HANDLING

Handle:

LLM unavailable

Invalid AI response

Pydantic validation failure

Transcription failure

Database failure

API timeout

Missing transcript

Empty transcript

Fact Find validation errors

Display understandable user-facing messages.

Never expose internal stack traces to the frontend.

---

# 44. DEVELOPMENT MODE

Provide a development mode that works without every AI dependency.

Support:

MockTranscriptionProvider

MockLLMProvider

Real OllamaProvider

This makes the entire application usable even when Ollama or faster-whisper is not installed.

Use environment configuration to select providers.

Example:

LLM_PROVIDER=mock

or

LLM_PROVIDER=ollama

TRANSCRIPTION_PROVIDER=mock

or

TRANSCRIPTION_PROVIDER=faster_whisper

---

# 45. LOCAL DEVELOPMENT

Provide Docker Compose for:

PostgreSQL

Backend

Frontend where appropriate

Ollama may be run separately if simpler.

Include:

README.md

Document:

Prerequisites

Installation

Environment variables

Database setup

Starting frontend

Starting backend

Starting Ollama

Downloading the selected model

Running tests

Using the sample transcript

---

# 46. FRONTEND PROJECT STRUCTURE

Use a scalable feature-oriented structure.

Example:

frontend/

src/

api/

components/

features/

clients/

meetings/

factFind/

review/

audit/

hooks/

pages/

schemas/

types/

utils/

App.tsx

main.tsx

Avoid placing all functionality inside App.tsx.

---

# 47. BACKEND PROJECT STRUCTURE

Use:

backend/

app/

api/

models/

schemas/

repositories/

services/

ai/

providers/

ollama_provider.py

mock_provider.py

transcription/

providers/

faster_whisper_provider.py

mock_provider.py

database/

core/

main.py

tests/

---

# 48. TESTING

Create automated tests for critical business logic.

At minimum test:

Financial extraction schema validation

AI response validation

Fact Find mapping

Advisor edit preservation

Rejected fields excluded from final contract

Missing information handling

Final Fact Find validation

Audit event creation

Test the supplied sample transcript.

---

# 49. OUT OF SCOPE

Do NOT build the following for this MVP:

Trading

Investment recommendations

Portfolio optimization

Product recommendations

Suitability determination

Financial projections

Account aggregation

Plaid integration

Production SSO

CRM integrations

Real-time streaming transcription

Advanced compliance surveillance

Automatic financial plan generation

Automated client-record updates

Native mobile applications

Complex workflow engines

Advanced analytics

The MVP should prove one experience extremely well:

**Conversation → Extraction → Review → Fact Find**

---

# 50. UX PRINCIPLES

The application should feel:

Professional

Trustworthy

Modern

Enterprise

Financial-services oriented

Data-rich but simple

Do not make it look like a generic AI chatbot.

The AI should feel like intelligence embedded inside the representative's existing workflow.

Use:

Client header

Sidebar navigation

Cards

Tabs

Tables

Confidence badges

Evidence panels

Review status indicators

Progress stepper

Clear warning and error states

---

# 51. CORE AI DESIGN PRINCIPLE

Every important extracted financial fact should answer three questions:

**What did the AI extract?**

Example:

401(k) Balance = $425,000

**Why did it extract it?**

Example evidence:

"My 401k is around $425,000."

**Has a human reviewed it?**

Example:

Needs Review

Accepted

Edited

Rejected

This traceability is a core product requirement.

---

# 52. RESPONSIBILITY BOUNDARIES

Keep these responsibilities separate:

React.js

=

User experience

React Hook Form

=

Form state

Zod

=

Frontend validation

TanStack Query

=

API/server-state management

shadcn/ui + Tailwind

=

UI components and styling

FastAPI

=

Backend APIs and application orchestration

faster-whisper

=

Speech-to-text

Qwen/Llama

=

Understanding the transcript and extracting structured information

Ollama

=

Running the LLM locally

Pydantic

=

Backend schema and AI-output validation

SQLAlchemy

=

Database access

PostgreSQL

=

Persistent storage

Do not merge these responsibilities unnecessarily.

---

# 53. BUILD ORDER

Implement the MVP in this order.

## Phase 1

React portal

Client search

Client profile

Fact Find workflow

Mock APIs

## Phase 2

FastAPI backend

PostgreSQL

SQLAlchemy

Client and Meeting APIs

## Phase 3

Transcript submission

Ollama integration

Qwen/Llama extraction

Pydantic validation

## Phase 4

Advisor Review UI

Accept/Edit/Reject

Evidence display

Missing information

## Phase 5

Fact Find mapping

Final review

Submission

Audit trail

## Phase 6

faster-whisper audio transcription

Do not block the core MVP on audio transcription.

The transcript-based workflow should work completely first.

---

# 54. DEFINITION OF DONE

The MVP is complete when the following scenario works end-to-end:

Search for Michael Thompson

→

Open Michael's profile

→

Click Start New Fact Find

→

Paste the sample meeting transcript

→

Click Analyze Meeting

→

FastAPI sends the transcript to the configured LLM

→

Qwen/Llama extracts structured financial information

→

Pydantic validates the extraction

→

React displays the extracted information

→

Advisor sees evidence and confidence

→

Advisor accepts, edits, or rejects each important fact

→

Application identifies missing information

→

Application maps approved data into FactFindContract

→

Advisor reviews the final Fact Find

→

Advisor checks the attestation

→

Advisor submits the Fact Find

→

PostgreSQL stores the final Fact Find

→

Application creates an audit history

→

Success page displays the completed Fact Find

This entire workflow must run locally using synthetic client information.

---

# 55. MOST IMPORTANT PRODUCT PRINCIPLE

The application exists to reduce manual data entry after a financial meeting.

The ideal user experience is:

**Talk naturally with the client.**

↓

**AI organizes the conversation.**

↓

**AI extracts financial facts with evidence.**

↓

**Financial Representative reviews instead of retyping.**

↓

**Approved facts become a structured Fact Find.**

↓

**Financial Representative performs final approval.**

↓

**Fact Find is saved.**

Optimize the MVP around this experience.

Build a functional application, not merely wireframes or static mockups.
