# Legal Document Assistant - Backend

Flask backend with SSE streaming and Gemini API integration.

## Architecture

This backend follows a modular architecture for better maintainability and scalability:

```
backend/
├── app.py                          # Main entry point (application factory)
├── config.py                       # Configuration and environment variables
├── models/
│   ├── __init__.py
│   └── schemas.py                  # Function definitions and data schemas
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py           # System prompts for the LLM
├── services/
│   ├── __init__.py
│   ├── document_service.py        # Document generation logic
│   └── conversation_service.py    # Conversation management
├── routes/
│   ├── __init__.py
│   └── chat.py                    # API endpoints
├── utils/
│   ├── __init__.py
│   └── streaming.py               # SSE streaming helpers
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── app.py.backup                  # Original monolithic version
```

### Module Responsibilities

- **config.py**: Centralized configuration management
- **models/**: Data structures and function schemas for Gemini
- **prompts/**: System prompts (separated for easy iteration)
- **services/**: Business logic (documents, conversations)
- **routes/**: API endpoints and request handling
- **utils/**: Shared utility functions

## Setup

1. Install Python 3.13.5 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Add your Gemini API key to `.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key
   ```

## Running

```bash
python app.py
```

Server will run on `http://localhost:5001`

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Main chat endpoint (SSE streaming)
- `GET /conversations/<id>` - Get conversation history
- `DELETE /conversations/<id>` - Delete conversation

## Function Calling

The backend implements three functions for the LLM:

1. **extract_information** - Extract structured data from conversation
2. **generate_document** - Generate legal documents
3. **apply_edits** - Apply edits to existing documents

## Supported Documents

- Director Appointment Resolutions
- Non-Disclosure Agreements (NDA)
- Employment Agreements

## Development

### Adding a New Document Type

1. Add generation logic in `services/document_service.py`:
   ```python
   @staticmethod
   def generate_new_document(data: Dict) -> str:
       # Implementation here
       pass
   ```

2. Update the `generate()` method to handle the new type

3. Update system prompt in `prompts/system_prompt.py` with requirements

4. No changes needed to routes or frontend!

### Modifying System Prompts

Edit `prompts/system_prompt.py` and see `PROMPT_ENGINEERING.md` for guidelines.

### Adding New Endpoints

1. Add route in `routes/chat.py` or create a new blueprint
2. Register blueprint in `app.py`

### Testing

```bash
# Test health endpoint
curl http://localhost:5001/health

# Test chat endpoint (requires frontend or curl with SSE)
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an NDA"}'
```

## Project Structure Benefits

✅ **Separation of Concerns** - Each module has a single responsibility
✅ **Easy Testing** - Services can be tested independently
✅ **Better Maintainability** - Changes are localized
✅ **Scalability** - Easy to add new features
✅ **Code Reusability** - Services can be imported anywhere
✅ **Clear Dependencies** - Module imports show relationships
