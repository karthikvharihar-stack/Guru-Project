# ॥ श्री दिग्विजय मूलरामो विजयते ॥
# Uttaradi Math — Guru Lekhana Seva Platform

An authentic, modern, and sacred digital platform dedicated to **Sri Hari-Vayu-Guru Smarana**, digital **Lekhana Seva** (mantra/nama writing), exploration of the **Guru Parampara** (the illustrious lineage of 42 pontiffs of Sri Uttaradi Math), and an AI-powered spiritual knowledge assistant (**Guru Jijnasa**).

---

## 🌟 Key Features

### 1. 📜 Complete Guru Parampara Archive
- Detailed spiritual profiles for all **42 Gurus** of Sri Uttaradi Math starting from **Jagadguru Sri Madhwacharya**.
- Traditional names, aradhana tithis, charitra (biographies), granthas/works, historical sources, and lineage navigation.

### 2. ✍️ Digital Lekhana Seva (Writing Pad)
- **Dual Writing Modes**:
  - **Typing Mode**: Real-time fuzzy-matching validation of typed stotras/mantras.
  - **Handwriting Pad**: Smooth HTML5 Canvas with adjustable stroke widths, eraser, and touch/stylus support.
- Configurable target counts (11, 28, 54, 108 japa counts).
- **Downloadable PDF Certificates**: Official, beautifully formatted Devotional Seva Acknowledgement certificates generated dynamically using ReportLab.

### 3. 🪔 Sacred Digital Deepa Altar
- Virtual deepa offering tray with real-time live offering count.
- Animated golden flickering diyas with devotee name & sankalpa tooltips.
- **Authentic Voice Blessing**: Plays the sacred chant of **H.H. Sri 1008 Sri Satyatma Teertha Swamiji** (*"Jai Shree Ram"*) upon offering.

### 4. 🪷 Guru Jijnasa (RAG-Powered Spiritual AI)
- Intelligent conversational assistant grounded in authentic Tattvavada / Dvaita Vedanta philosophy.
- **Retrieval-Augmented Generation (RAG)** using **Google Gemini** + **ChromaDB** local vector embeddings.
- Strict anti-hallucination guardrails adhering to verified sampradaya texts.
- **Voice Query Support**: Voice input transcription using Gemini Multimodal Audio API.

### 5. 🛡️ User & Admin Portals
- **Devotee Accounts**: Multi-language preference (English, Kannada, Sanskrit), session history, and cumulative seva progress dashboard (`/my-seva`).
- **Admin Management**: Full CRUD interface for Gurus, theological works, library books, pravachana media, calendar events, and knowledge-base indexing.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Custom Sacred Temple Theme), Vanilla JavaScript (ES6+), HTML5 Canvas 2D API, Web Audio API
- **Backend**: Python 3.14, Flask 3.0.3, Flask-SQLAlchemy 3.1.1, Flask-Login, Flask-WTF, Flask-Limiter, ReportLab
- **AI & Vector DB**: Google Gemini API (`google-generativeai`), ChromaDB, `sentence-transformers`
- **Database**: SQLite (Development) / MySQL & MariaDB compatible (Production)
- **Audio Processing**: `yt-dlp`, `imageio-ffmpeg`, `soundfile`, `numpy`

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Guru-Project.git
cd Guru-Project
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to provide your configuration (such as `SECRET_KEY`, `USE_SQLITE=True`, and optional `GEMINI_API_KEY`).

### 5. Run the Application
```bash
python run.py
```
Or double-click **`start_server.bat`** on Windows.

Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running Automated Tests

The application includes an end-to-end test suite verifying all routes, database operations, and user flows:
```bash
python test_e2e.py
```
*(All 30 tests pass out of the box).*

---

## 📁 Project Structure

```text
Guru-Project/
├── app/
│   ├── models/          # 15 SQLAlchemy database models
│   ├── routes/          # 11 Flask blueprints (main, auth, guru, lekhana, etc.)
│   ├── services/        # AI (Gemini RAG), PDF generation, Lekhana services
│   ├── static/          # CSS, JS, sacred audio clips, and guru imagery
│   └── templates/       # Jinja2 HTML templates for all views
├── instance/            # Local SQLite database
├── uploads/             # Media, PDFs, and deepa JSON store
├── config.py            # Environment configurations
├── run.py               # Flask application entry point
├── start_server.bat     # 1-click Windows launcher
├── requirements.txt     # Python package dependencies
└── test_e2e.py          # End-to-end test suite
```

---

## 📜 Disclaimer

This is an independent devotional and educational digital platform created with reverence for Sri Hari-Vayu-Guru Smarana and Sri Uttaradi Math Peetham. It is not an official commercial product.
