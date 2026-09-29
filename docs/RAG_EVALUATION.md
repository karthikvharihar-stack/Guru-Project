# Guru Jijnasa — RAG Architecture & Evaluation Framework

This document outlines the **Retrieval-Augmented Generation (RAG)** architecture, chunking methodology, anti-hallucination guardrails, and graceful degradation strategies implemented in **Guru Jijnasa**, the spiritual AI assistant of the Guru Parampara platform.

---

## 1. System Architecture Overview

```
                      Devotee Query (Text or Voice)
                                   │
                                   ▼
             ┌───────────────────────────────────────────┐
             │   Query Preprocessing & Entity Matcher     │
             │   - Audio transcription via Gemini        │
             │   - Numeric order extraction (#1 - #42)   │
             │   - Canonized Guru name alias resolution   │
             └─────────────────────┬─────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌─────────────────────────┐
       │ Vector Search Pipeline │    │ Deterministic SQL DB    │
       │ (ChromaDB + Cosine)    │    │ (Verified Records Only) │
       └────────────┬───────────┘    └────────────┬────────────┘
                    │                             │
                    ▼                             ▼
       ┌────────────────────────────────────────────────────────┐
       │               Anti-Hallucination Gate                   │
       │  - Vector Distance Check (Threshold: dist < 0.40)      │
       │  - Strict Lekhana Isolation (SQL-only, never from LLM) │
       │  - System Prompt Constraints & Grounding Injection    │
       └───────────────────────────┬────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
       [Confidence Valid]                   [Confidence Low / Fail]
                 │                                   │
                 ▼                                   ▼
       ┌───────────────────┐               ┌───────────────────┐
       │ Google Gemini LLM │               │ Local Deterministic│
       │ (Grounding Window)│               │ Knowledge Engine  │
       └─────────┬─────────┘               └─────────┬─────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                    Devotee-Facing Structured Answer
                    + Verified Source Attributions
```

---

## 2. Text Chunking & Embedding Strategy

Spiritual texts (Sarvamoola Granthas, Gurucharitra, and Stotra literature) have high theological density where sentence-level truncations can alter philosophical meaning.

### Chunking Parameters:
- **Strategy**: Recursive Character Text Chunking preserving paragraph (`\n\n`), sentence (`. `), and philosophical verse markers.
- **Chunk Size**: `600–800 characters` (~120–160 tokens).
- **Chunk Overlap**: `100 characters` (sliding window overlap) to guarantee cross-boundary continuity of philosophical arguments.
- **Metadata Stamping**: Every chunk is injected with contextual metadata tags before vectorization:
  ```json
  {
    "guru_order": 6,
    "guru_name": "Sri Jayateertha",
    "traditional_title": "Sri Teekacharya",
    "topic_category": "Nyayasudha / Commentary",
    "source_document": "Jayateertha Vijaya & Sriman Nyayasudha",
    "verification_status": "verified"
  }
  ```
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` / Google Embeddings API, producing normalized 384-dimensional dense vectors stored in a local persistent ChromaDB collection.

---

## 3. Strict Anti-Hallucination Guardrails

Because this application serves sacred spiritual and historical content, **zero tolerance for hallucination** is enforced through architectural constraints:

### 1. Sacred Lekhana Text Isolation
- **Rule**: The AI model is strictly prohibited from generating, completing, or guessing sacred Lekhana mantras.
- **Enforcement**: Sacred Lekhana mantras are retrieved exclusively through direct relational SQL queries (`Guru.lekhana_text`) verified by administrators. Even in generative Gemini calls, the prompt explicitly instructs:
  > *"Lekhana text must only be quoted from verified database records. Never invent or synthesize sacred mantras."*

### 2. Strict Negative Constraint Prompting
- Prompts include system-level guardrails:
  - If a requested historical event or date is unrecorded in canonical texts, the model must explicitly respond that it is not documented rather than extrapolating.
  - No synthetic pontiffs, dates, or lineages can be hallucinated.

### 3. Source Attribution Requirement
- Every response must return structured metadata indicating whether the information originated from:
  - `database`: Direct verified administrative records.
  - `biography`: Canonical Guru Charitra.
  - `granthas`: Documented Sarvamoola or philosophical commentaries.

---

## 4. Handling Low Vector Scores & ChromaDB Failures

A critical requirement in production RAG systems is handling out-of-domain queries, noisy questions, or vector match failures.

### Multi-Stage Fallback Cascade:

```
Step 1: ChromaDB Query
   │
   ├── Vector Distance < 0.40 (High Relevance) ──> Inject into Gemini Grounded Context
   │
   └── Vector Distance >= 0.40 OR ChromaDB Offline ──> Trigger Fallback Cascade
         │
         ├── Step 2: Entity & Order Matcher
         │     ├── Matches Guru Order (#1 to #42)
         │     ├── Matches Guru Name / Alias ("Teekacharya", "Satyatma Tirtha")
         │     └── Matches Core Tenets (Pancha Bheda, Moola Rama, Lekhana)
         │           └──> Return Deterministic Knowledge Engine Answer
         │
         └── Step 3: Out-of-Domain Graceful Fallback
               └──> Return Structured Guidance Prompt (No fabricated information)
```

1. **Distance Thresholding**:
   - Queries with cosine distance $\ge 0.40$ (low similarity) are discarded from vector context injection to prevent grounding on irrelevant scriptures.

2. **Deterministic Fallback Engine (`_local_knowledge_engine`)**:
   - If ChromaDB is unavailable, unindexed, or yields insufficient confidence, execution seamlessly falls back to the deterministic local knowledge engine in `app/services/ai_service.py`.
   - Contains pre-verified canonical summaries covering:
     - All 42 Peethadhipatis by number, birth name, sannyasa name, and aradhana.
     - Foundational philosophical pillars (Dvaita, Pancha Bheda, Vayu Jeevottamatva).
     - Divine lineage of Sri Moola Rama and the rituals of Sri Uttaradi Math.

3. **Graceful Uncertainty Acknowledgement**:
   - If a devotee asks a question completely outside the scope (e.g., modern politics or unverified folklore), the system does not fabricate an answer.
   - It politely explains the scope of the archive and suggests related canonical questions the devotee can ask.

---

## 5. Evaluation Benchmarks

The RAG engine is continuously validated against a golden dataset of canonical queries:

| Test Category | Example Query | Expected Behavior | Verification Status |
|---------------|---------------|-------------------|---------------------|
| **Order Query** | *"Who is the 6th guru?"* | Retrieves Sri Jayateertha without hallucinating order | ✅ Passed |
| **Alias Resolution** | *"Tell me about Teekacharya"* | Resolves alias to Sri Jayateertha (#06) | ✅ Passed |
| **Philosophical Tenet** | *"Explain Pancha Bheda"* | Lists all 5 eternal distinctions verbatim | ✅ Passed |
| **Lekhana Isolation** | *"Give me the mantra for guru 1"* | Fetches verified text from DB; does not hallucinate | ✅ Passed |
| **Out-of-Domain Query** | *"What is quantum entanglement?"* | Graceful fallback without fabricating theological stance | ✅ Passed |
| **Zero Vector Match** | Empty / random string input | Handled gracefully with prompt suggestions | ✅ Passed |

---

## 6. Summary

Through hybrid retrieval (Dense Vector Search + Deterministic Entity Matching), strict Lekhana isolation, and multi-stage fallback cascades, **Guru Jijnasa** provides a high-reliability, spiritually reverent AI experience that prevents hallucinations while maintaining accessibility for devotees.
