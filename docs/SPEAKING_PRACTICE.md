# Speaking Practice Feature Documentation

## Overview
The Speaking Practice feature allows users to record audio responses to reading materials and receive AI-generated feedback on their pronunciation, fluency, and accuracy. This feature is integrated into the "English Practice" module of the BharatGen Yojaka platform.

## Architecture

### Frontend
- **File:** `templates/english_practice.html`
- **Technology:** HTML5, JavaScript (MediaRecorder API)
- **Flow:**
    1. User switches to the "Speaking Practice" tab.
    2. Browser requests microphone permission.
    3. User records audio using `MediaRecorder`.
    4. Audio is converted to a Blob (WAV format).
    5. `FormData` is sent to the backend via `fetch` API.

### Backend
- **Endpoint:** `/api/learning/contents/{id}/submit_speaking/`
- **View:** `apps.learning.views.ContentViewSet.submit_speaking`
- **Provider:** `apps.rag.providers.gemini_provider.GeminiProvider`

#### Data Flow
1. **Upload:** The frontend uploads the audio file (WAV/MP3) to the Django view.
2. **Processing:**
    - The view saves the audio to a temporary file.
    - It initializes the `GeminiProvider`.
    - Calls `evaluate_speaking_audio(audio_path, reference_text)`.
3. **AI Evaluation (Gemini):**
    - The provider uploads the audio file directly to Google Gemini using `genai.upload_file`.
    - A multimodal prompt is sent to Gemini:
        - **Input:** Audio File + Reference Text + Rubric
        - **Output:** JSON object containing `{ "grade": <0-100>, "feedback": "..." }`
4. **Response:** The JSON result is returned to the frontend for display.

## Configuration

### Prerequisites
- **Gemini API Key:** Required for audio processing.
    - Set `GEMINI_API_KEY` in your `.env` file.
- **HTTPS or Localhost:** Browsers require a secure context (`https://` or `localhost`) to access the microphone.

### Development Setup (HTTPS)
If accessing from a remote machine (not localhost), you must use HTTPS.
1. Install `django-sslserver`: `pip install django-sslserver`
2. Run server: `python manage.py runsslserver 0.0.0.0:8090`
3. Access via `https://<your-ip>:8090` and accept the self-signed certificate warning.

## Future Improvements / Alternatives
- **Offline Support:** Currently relies on Gemini. To support purely local/offline usage, we can implement a pipeline using **Whisper** (for Speech-to-Text) + **Llama/Ollama** (for Text Evaluation).

