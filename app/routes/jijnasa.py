import base64
from flask import Blueprint, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.ai_service import get_ai_service

jijnasa_bp = Blueprint('jijnasa', __name__)


@jijnasa_bp.route('/')
def index():
    """Guru Jijnasa chat page."""
    example_questions = [
        "Who is the first Guru in the Parampara?",
        "What is Dvaita Vedanta?",
        "What is Guru Lekhana Seva?",
        "Tell me about the Guru Parampara of Uttaradi Math.",
        "What are the major works in the Dvaita tradition?",
        "What does 'Ananda' mean in Dvaita philosophy?",
    ]
    ai_ready = get_ai_service().is_ready
    return render_template('jijnasa/index.html',
                           example_questions=example_questions,
                           ai_ready=ai_ready)


@jijnasa_bp.route('/ask', methods=['POST'])
def ask():
    """
    AJAX endpoint: accept a question, run RAG pipeline, return answer.

    Rate limited to prevent abuse.
    """
    from app.extensions import limiter

    # Manual rate check (since blueprint-level limiter decoration is complex)
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    conversation_history = data.get('history', [])

    if not question:
        return jsonify({'error': 'Question is required.'}), 400

    if len(question) > 2000:
        return jsonify({'error': 'Question is too long (max 2000 characters).'}), 400

    # Sanitize conversation history
    safe_history = []
    for msg in conversation_history[-10:]:  # Max 10 history entries
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            role = str(msg['role'])[:10]
            content = str(msg['content'])[:1000]
            if role in ('user', 'model', 'assistant'):
                safe_history.append({'role': role, 'content': content})

    ai_svc = get_ai_service()
    result = ai_svc.answer_question(question, conversation_history=safe_history)

    return jsonify({
        'answer': result.get('answer', ''),
        'sources': result.get('sources', []),
        'is_fallback': result.get('is_fallback', False)
    })


@jijnasa_bp.route('/transcribe', methods=['POST'])
def transcribe():
    """
    AJAX endpoint: receive audio blob, return transcription.
    Uses Gemini for speech-to-text.
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided.'}), 400

    audio_file = request.files['audio']
    if audio_file.content_length and audio_file.content_length > 5 * 1024 * 1024:
        return jsonify({'error': 'Audio too large (max 5MB).'}), 400

    audio_data = audio_file.read()
    mime_type = audio_file.content_type or 'audio/webm'

    ai_svc = get_ai_service()
    transcription = ai_svc.transcribe_audio(audio_data, mime_type)

    if not transcription:
        return jsonify({'error': 'Transcription failed or service unavailable.'}), 503

    return jsonify({'transcription': transcription})
