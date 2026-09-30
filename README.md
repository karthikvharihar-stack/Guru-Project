# Parampara-AI

A RAG-powered knowledge engine for Guru Parampara — combining a dual-mode writing pad, historical archives, and a grounded AI assistant that never hallucinates Guru names or sacred texts.

**Live:** https://guru-lekhana-seva.onrender.com

## What it does

- **Writing Pad** — Type or handwrite (HTML5 Canvas) a Guru's traditional text. Validates input with fuzzy matching before counting progress.
- **Guru Archive** — Biographies, titles, and works for 42 historical pontiffs from Sri Madhwacharya onwards.
- **Guru Jijnasa** — Ask questions about Guru Parampara. Answers come from ChromaDB vector retrieval + Gemini, with a local fallback to prevent hallucination.
- **Digital Deepa** — Interactive offering with Swamiji's audio.
- **Seva Certificates** — Downloadable PDF certificates generated via ReportLab.

## Stack

Python 3.11 · Flask · SQLAlchemy · Google Gemini · ChromaDB · sentence-transformers · HTML5 Canvas · ReportLab

## Run locally

```bash
git clone https://github.com/karthikvharihar-stack/Guru-Project.git
cd Guru-Project
pip install -r requirements.txt
cp .env.example .env   # add your GEMINI_API_KEY
python run.py
```

## Docs

[RAG Architecture & Evaluation](docs/RAG_EVALUATION.md)

## License

[MIT](LICENSE)
