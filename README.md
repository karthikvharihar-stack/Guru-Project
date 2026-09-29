# Guru Lekhana Seva

A full-stack web platform for mantra writing (Lekhana Seva), archival records of the 42 Guru Parampara, and a grounded AI assistant (Guru Jijnasa) answering queries on Dvaita Vedanta philosophy.

## Features

- **Digital Writing Pad**: Dual-mode writing interface (keyboard typing with fuzzy text validation, and HTML5 Canvas handwriting pad with touch/stylus support).
- **Guru Parampara Archive**: Biographies, traditional titles, and works for 42 historical pontiffs starting from Sri Madhwacharya.
- **Devotional Altar**: Interactive digital deepa offering with audio playback.
- **Guru Jijnasa (AI Assistant)**: Grounded question-answering using Google Gemini and ChromaDB vector retrieval, with local fallback for verified records to prevent hallucinations.
- **Certificates & Progress**: Downloadable Seva completion certificates generated via ReportLab and user progress tracking.

## Tech Stack

- **Backend**: Python 3.11/3.12, Flask, Flask-SQLAlchemy, Flask-Login, ReportLab
- **Frontend**: HTML5 Canvas, CSS3, Vanilla JavaScript (ES6)
- **Database**: SQLite (local) / MySQL compatible
- **AI / Embeddings**: Google Gemini API, ChromaDB, sentence-transformers

## Getting Started

### 1. Clone & Set Up
```bash
git clone https://github.com/karthikvharihar-stack/Guru-Project.git
cd Guru-Project

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Variables
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```

### 3. Run Locally
```bash
python run.py
```
Or double-click `start_server.bat` on Windows.  
Once running, open `http://127.0.0.1:5000` in your browser.

## Tests

Run the test suite:
```bash
python test_e2e.py
```

## Documentation

- [RAG Architecture & Evaluation Notes](docs/RAG_EVALUATION.md)

## License

[MIT](LICENSE)
