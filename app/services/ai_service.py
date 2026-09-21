"""
Guru Jijnasa AI Service — RAG-based question answering.

Architecture:
  User question
    → Embed with sentence-transformers
    → Similarity search in ChromaDB
    → Retrieve Guru data from MySQL
    → Build grounded prompt for Gemini
    → Return answer + source attribution

IMPORTANT CONTENT RULES (enforced in prompt):
  - Never invent Guru names, Lekhana, dates, or quotations.
  - Never present AI translation as authoritative.
  - Cite sources for every factual claim.
  - Say "not available" when data is missing.
  - Lekhana text is ALWAYS retrieved from the database — never generated.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# --- Optional heavy dependencies (graceful fallback if not installed) ---
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not installed. Vector search disabled.")

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Embeddings disabled.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. AI responses will use fallback.")


class GuruJijnasaService:
    """
    RAG-based AI assistant for Guru Parampara knowledge.
    Grounded in verified database content + indexed documents.
    """

    SYSTEM_PROMPT = """You are Guru Jijnasa, a respectful and knowledgeable assistant for the Uttaradi Math Guru Parampara digital platform.

Your role:
- Provide accurate information about the Guru Parampara of Uttaradi Math.
- Explain Dvaita Vedanta philosophy clearly and respectfully.
- Help devotees find information about Gurus, their works, and teachings.

STRICT CONTENT RULES — you MUST follow these:
1. NEVER invent or fabricate Guru names, lineage details, or succession information.
2. NEVER generate or invent Lekhana (sacred devotional text). If asked about Lekhana, only use the exact text provided in the context. If not provided, say: "The verified Lekhana for this Guru is available on their profile page. I cannot generate sacred text from memory."
3. NEVER invent dates (birth, aradhana, historical events).
4. NEVER invent quotations and attribute them to historical Gurus or scholars.
5. If information is not in the provided context, say clearly: "I don't have verified information about this. Please consult authoritative sources or the Math directly."
6. Distinguish between: (a) information from verified database records, (b) information from uploaded documents, and (c) your general training knowledge.
7. For philosophical explanations, you may draw on general knowledge but clearly label it as a general explanation, not an authoritative religious ruling.
8. Always maintain a respectful, calm, devotional tone.
9. If asked about official Math communications, events, or practices, direct the user to contact Uttaradi Math Peetham directly.
10. You are an informational assistant — not a spiritual authority.

When you have sources, always end your response with a "Sources:" section listing them.
If you have no sources, say so clearly."""

    def __init__(self):
        self._embedding_model = None
        self._chroma_client = None
        self._collection = None
        self._gemini_model = None
        self._initialized = False

        # Try to initialize
        self._init_gemini()
        self._init_chroma()

    def _init_gemini(self):
        """Initialize Gemini API."""
        if not GEMINI_AVAILABLE:
            return
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. AI responses disabled.")
            return
        try:
            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=self.SYSTEM_PROMPT
            )
            logger.info("Gemini initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

    def _init_chroma(self):
        """Initialize ChromaDB and sentence-transformer embedding model."""
        if not CHROMA_AVAILABLE or not ST_AVAILABLE:
            return
        try:
            chroma_path = os.path.join(os.path.dirname(__file__), '../../ai/chroma_db')
            chroma_path = os.path.abspath(chroma_path)
            os.makedirs(chroma_path, exist_ok=True)

            self._chroma_client = chromadb.PersistentClient(path=chroma_path)
            self._collection = self._chroma_client.get_or_create_collection(
                name="guru_knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )

            # Load embedding model (small, fast, multilingual)
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._initialized = True
            logger.info("ChromaDB + SentenceTransformer initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    @property
    def is_ready(self):
        """Check if the AI service is operational."""
        return self._gemini_model is not None

    def embed_text(self, text: str) -> Optional[list]:
        """Embed text using sentence-transformers."""
        if not self._embedding_model:
            return None
        try:
            return self._embedding_model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def add_document(self, doc_id: str, title: str, chunks: list[dict]) -> bool:
        """
        Add document chunks to ChromaDB.
        chunks: list of {'text': str, 'index': int}
        """
        if not self._collection or not self._embedding_model:
            return False
        try:
            ids = [f"doc_{doc_id}_chunk_{c['index']}" for c in chunks]
            texts = [c['text'] for c in chunks]
            metadatas = [{'doc_id': str(doc_id), 'title': title, 'chunk_index': c['index']} for c in chunks]

            # Batch embed
            embeddings = self._embedding_model.encode(texts).tolist()

            self._collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {e}")
            return False

    def search_knowledge_base(self, query: str, n_results: int = 5) -> list[dict]:
        """Search ChromaDB for relevant chunks."""
        if not self._collection or not self._embedding_model:
            return []
        try:
            query_embedding = self._embedding_model.encode(query).tolist()
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self._collection.count() or 1),
                include=['documents', 'metadatas', 'distances']
            )
            chunks = []
            for i, doc in enumerate(results['documents'][0]):
                chunks.append({
                    'text': doc,
                    'title': results['metadatas'][0][i].get('title', 'Unknown'),
                    'distance': results['distances'][0][i]
                })
            return chunks
        except Exception as e:
            logger.error(f"ChromaDB search error: {e}")
            return []

    def _get_guru_context(self, question: str) -> str:
        """
        Query the MySQL database for relevant Guru information.
        Returns a formatted string of verified Guru data.
        """
        try:
            from app.models.guru import Guru
            gurus = Guru.query.filter_by(is_verified=True, is_active=True).all()
            if not gurus:
                return "No verified Guru information is currently available in the database."

            # Simple keyword matching to find relevant gurus
            question_lower = question.lower()
            relevant_gurus = []

            for guru in gurus:
                score = 0
                name_lower = guru.name.lower()
                # Check if guru name is mentioned
                if any(word in question_lower for word in name_lower.split()):
                    score += 10
                if 'lekhana' in question_lower:
                    score += 2
                if 'all' in question_lower or 'list' in question_lower or 'parampara' in question_lower:
                    score += 5
                if score > 0:
                    relevant_gurus.append((score, guru))

            # If no specific match, return brief list of all gurus
            if not relevant_gurus:
                guru_list = ', '.join(g.name for g in gurus[:10])
                return f"Verified Gurus in the Parampara: {guru_list}."

            # Format relevant gurus
            relevant_gurus.sort(key=lambda x: x[0], reverse=True)
            context_parts = []

            for _, guru in relevant_gurus[:3]:
                parts = [f"## Guru: {guru.name}"]
                if guru.traditional_name:
                    parts.append(f"Traditional Name: {guru.traditional_name}")
                parts.append(f"Order in Parampara: {guru.guru_order}")
                if guru.short_description:
                    parts.append(f"Description: {guru.short_description}")
                if guru.biography:
                    parts.append(f"Biography: {guru.biography[:500]}...")
                if guru.birth_date:
                    parts.append(f"Birth/Era: {guru.birth_date}")
                if guru.aradhana_date:
                    parts.append(f"Aradhana: {guru.aradhana_date}")

                # Lekhana — ALWAYS from DB, never generated
                if guru.lekhana_text and '[PLACEHOLDER' not in guru.lekhana_text:
                    parts.append(f"Verified Lekhana: {guru.lekhana_text}")
                    if guru.lekhana_english:
                        parts.append(f"Lekhana (English): {guru.lekhana_english}")
                else:
                    parts.append("Lekhana: [Not yet verified by administrator]")

                context_parts.append('\n'.join(parts))

            return '\n\n'.join(context_parts)

        except Exception as e:
            logger.error(f"Error getting guru context: {e}")
            return "Database context unavailable."

    def answer_question(self, question: str, conversation_history: list = None) -> dict:
        """
        Main RAG pipeline: question → context retrieval → Gemini → answer + sources.

        Returns:
            dict with keys: answer, sources, is_fallback
        """
        if conversation_history is None:
            conversation_history = []

        if not self._gemini_model:
            return {
                'answer': "Guru Jijnasa is currently unavailable. The AI service is not configured. Please set the GEMINI_API_KEY in your .env file.",
                'sources': [],
                'is_fallback': True
            }

        sources = []
        context_parts = []

        # 1. Get relevant DB context
        db_context = self._get_guru_context(question)
        if db_context:
            context_parts.append(f"=== VERIFIED DATABASE RECORDS ===\n{db_context}")
            sources.append({'title': 'Verified Guru Database', 'type': 'database'})

        # 2. Search knowledge base
        kb_chunks = self.search_knowledge_base(question, n_results=4)
        if kb_chunks:
            kb_text = '\n\n'.join([f"[From: {c['title']}]\n{c['text']}" for c in kb_chunks])
            context_parts.append(f"=== UPLOADED KNOWLEDGE BASE ===\n{kb_text}")
            for chunk in kb_chunks:
                if not any(s['title'] == chunk['title'] for s in sources):
                    sources.append({'title': chunk['title'], 'type': 'document'})

        # 3. Build the grounded prompt
        context_text = '\n\n'.join(context_parts) if context_parts else "No specific verified context found."

        prompt = f"""VERIFIED CONTEXT (use this as your primary source):
{context_text}

---
USER QUESTION: {question}

Answer the question based on the verified context above. If the context does not contain the answer, say clearly that you don't have verified information about this topic. Do not invent information."""

        # 4. Build conversation history for Gemini
        try:
            history = []
            for msg in conversation_history[-6:]:  # Keep last 3 exchanges
                history.append({'role': msg['role'], 'parts': [msg['content']]})

            chat = self._gemini_model.start_chat(history=history)
            response = chat.send_message(prompt)
            answer_text = response.text

            return {
                'answer': answer_text,
                'sources': sources,
                'is_fallback': False
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            error_type = type(e).__name__
            if 'quota' in str(e).lower() or 'rate' in str(e).lower():
                msg = "Guru Jijnasa is receiving too many requests. Please try again in a moment."
            elif 'api_key' in str(e).lower() or 'auth' in str(e).lower():
                msg = "Guru Jijnasa is not configured correctly. Please contact the administrator."
            else:
                msg = "Guru Jijnasa encountered an error. Please try again."

            return {
                'answer': msg,
                'sources': [],
                'is_fallback': True,
                'error': error_type
            }

    def get_lekhana_for_guru(self, guru_name_or_slug: str) -> dict:
        """
        Retrieve verified Lekhana from database for a Guru.
        NEVER generates from LLM — always from DB.
        """
        try:
            from app.models.guru import Guru
            guru = (
                Guru.query.filter_by(slug=guru_name_or_slug, is_verified=True).first()
                or Guru.query.filter(Guru.name.ilike(f'%{guru_name_or_slug}%'), Guru.is_verified == True).first()
            )
            if not guru:
                return {
                    'found': False,
                    'message': f'No verified Guru found matching "{guru_name_or_slug}".'
                }
            if not guru.lekhana_text or '[PLACEHOLDER' in guru.lekhana_text:
                return {
                    'found': True,
                    'guru_name': guru.name,
                    'lekhana_available': False,
                    'message': 'The Lekhana for this Guru is awaiting administrator verification.'
                }
            return {
                'found': True,
                'guru_name': guru.name,
                'guru_order': guru.guru_order,
                'lekhana_available': True,
                'lekhana_text': guru.lekhana_text,
                'lekhana_sanskrit': guru.lekhana_sanskrit,
                'lekhana_kannada': guru.lekhana_kannada,
                'lekhana_english': guru.lekhana_english,
            }
        except Exception as e:
            logger.error(f"Error fetching lekhana: {e}")
            return {'found': False, 'message': 'Database error.'}

    def index_guru_data(self) -> dict:
        """
        Index all verified Guru bios and descriptions into ChromaDB
        so they can be retrieved during RAG.
        """
        if not self._collection or not self._embedding_model:
            return {'success': False, 'message': 'ChromaDB not available.'}

        try:
            from app.models.guru import Guru
            gurus = Guru.query.filter_by(is_verified=True, is_active=True).all()
            indexed = 0

            for guru in gurus:
                chunks = []
                # Chunk 1: Basic info
                info = f"Guru: {guru.name}. Order: {guru.guru_order}."
                if guru.traditional_name:
                    info += f" Traditional name: {guru.traditional_name}."
                if guru.short_description:
                    info += f" {guru.short_description}"
                chunks.append({'text': info, 'index': 0})

                # Chunk 2: Biography (split if long)
                if guru.biography:
                    bio_chunks = [guru.biography[i:i+500] for i in range(0, len(guru.biography), 500)]
                    for j, bio_chunk in enumerate(bio_chunks):
                        chunks.append({'text': bio_chunk, 'index': j + 1})

                self.add_document(
                    doc_id=f"guru_{guru.id}",
                    title=guru.name,
                    chunks=chunks
                )
                indexed += 1

            return {'success': True, 'indexed': indexed}
        except Exception as e:
            logger.error(f"Error indexing guru data: {e}")
            return {'success': False, 'message': str(e)}

    def transcribe_audio(self, audio_data: bytes, mime_type: str = 'audio/webm') -> str:
        """
        Transcribe audio to text using Gemini's multimodal capability.
        Returns transcribed text or empty string on failure.
        """
        if not self._gemini_model:
            return ''
        try:
            # Use Gemini to transcribe
            audio_part = {'mime_type': mime_type, 'data': audio_data}
            response = self._gemini_model.generate_content([
                "Transcribe the following audio to text. Return only the transcription, nothing else.",
                audio_part
            ])
            return response.text.strip()
        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            return ''


# Module-level singleton
_service_instance = None

def get_ai_service() -> GuruJijnasaService:
    """Get or create the singleton AI service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = GuruJijnasaService()
    return _service_instance
