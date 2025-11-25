# Legal Document Assistant

An AI-powered legal document generation system that uses streaming SSE responses, LLM function calling, and sophisticated prompt engineering to help users create professional legal documents through natural conversation.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13.5-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-15.5.6-black.svg)

## 🎯 Project Overview

This application demonstrates:

1. **Server-Sent Events (SSE) Streaming (30%)** - Real-time token-by-token streaming of AI responses
2. **LLM Function/Tool Calling (40%)** - Three sophisticated functions for information extraction, document generation, and editing
3. **Strong System Prompts (30%)** - Carefully engineered prompts with edge case handling and context maintenance

## 📁 Project Structure

```
lexiden-tech-challenge/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/ # React components
│   │   └── lib/       # Utilities
│   └── package.json
├── backend/           # Flask backend API
│   ├── app.py        # Main Flask application
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## 🚀 Features

### Core Features (All Implemented)

✅ **SSE Streaming**
- Real-time token-by-token streaming of LLM responses
- Connection management and error recovery
- Streams both conversational responses and document generation
- Visual feedback with typing indicators

✅ **Function Calling**
Three intelligent functions:
1. **extract_information** - Extracts structured data from natural language
2. **generate_document** - Creates complete legal documents
3. **apply_edits** - Applies precise modifications to existing documents

✅ **System Prompts**
- Comprehensive role definition
- Clear function usage guidelines
- Edge case handling
- Context maintenance across conversation

### Nice-to-Have Features (All Included)

✅ **Structured Outputs** - Forced structured outputs through function calling
✅ **Conversation Memory** - Context maintained across messages within a session
✅ **Document Preview** - Live document preview with real-time updates
✅ **Edit Highlighting** - Visual indication of changes
✅ **Smooth UX** - Framer Motion animations and responsive design

### Supported Document Types

1. **Director Appointment Resolutions**
   - Director name, effective date, committee assignments
   - Professional formatting with legal structure

2. **Non-Disclosure Agreements (NDA)**
   - Party names, terms, confidentiality obligations
   - Standard NDA clauses and provisions

3. **Employment Agreements**
   - Employee details, position, compensation
   - Terms and conditions of employment

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **LLM**: Google Gemini Flash 2.5 (via `google-generativeai`)
- **Streaming**: Server-Sent Events (SSE)
- **CORS**: Flask-CORS for cross-origin requests

### Frontend
- **Framework**: Next.js 15.5.6 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom red theme
- **UI Components**:
  - Lucide React (icons)
  - Framer Motion (animations)
  - clsx + tailwind-merge (class management)
- **Build Tool**: Turbopack

### Design System
- **Colors**: Light Red (#FCA5A5), Red (#EF4444), Deep Red (#991B1B)
- **Theme**: Inspired by transparently.ai
- **UI Style**: Clean, generous whitespace, rounded corners (xl), subtle shadows

## 📋 Prerequisites

- **Python**: 3.13.5 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Gemini API Key**: Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd lexiden-tech-challenge
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Add your Gemini API key to .env
# GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

Backend will run on `http://localhost:5001`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### Access the Application

Open your browser and navigate to `http://localhost:3000`

## 💡 Usage Examples

### Example 1: Creating a Director Appointment

**User:** "I need to appoint John Smith as a director"

**AI:**
- Extracts information using `extract_information` function
- Asks for missing details (effective date, committees)
- Generates document using `generate_document` function
- Streams the complete resolution

### Example 2: Creating an NDA

**User:** "I need an NDA between Acme Corp and John Doe"

**AI:**
- Identifies document type
- Gathers required information (effective date, term)
- Generates professional NDA
- Offers to make modifications

### Example 3: Editing a Document

**User:** "Change the effective date to January 1st"

**AI:**
- Uses `apply_edits` function
- Updates the specific field
- Shows what changed
- Streams updated document

## 🏗️ Architecture

### SSE Streaming Implementation

The backend implements SSE streaming through Flask's `Response` with `stream_with_context`:

```python
def generate():
    for chunk in response:
        yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
```

The frontend consumes the stream using the Fetch API with a ReadableStream:

```typescript
const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
    const { done, value } = await reader.read()
    if (done) break
    // Process chunk
}
```

### Function Calling Flow

1. User sends message
2. Backend forwards to Gemini with function definitions
3. Gemini decides if a function should be called
4. Backend executes the function
5. Backend sends function result back to Gemini
6. Gemini generates natural language response
7. Response is streamed to frontend

### Memory Management

Conversations are stored in-memory with unique IDs:
- `conversations[id]` - Message history
- `conversation_documents[id]` - Current document state

## 📖 System Prompt Engineering

### Prompt Structure

The system prompt includes:

1. **Role Definition** - Establishes AI as legal document assistant
2. **Function Guidelines** - Detailed instructions for each function
3. **Conversation Guidelines** - Natural interaction principles
4. **Edge Case Handling** - Strategies for ambiguity and errors

### Key Design Decisions

1. **Detailed Function Descriptions** - Each function has clear use cases and examples
2. **Conversational Tone** - Professional yet approachable language
3. **Proactive Clarification** - AI asks for missing information
4. **Context Awareness** - References previous exchanges
5. **Error Handling** - Graceful degradation for edge cases

See [PROMPT_ENGINEERING.md](./PROMPT_ENGINEERING.md) for detailed prompt iterations and improvements.

## 🧪 Testing the Application

### Test Scenario 1: Basic Document Generation

1. Start a conversation: "I need a director appointment"
2. Provide information when asked
3. Verify document appears in preview
4. Test download functionality

### Test Scenario 2: Document Editing

1. Generate a document first
2. Request an edit: "Change the date to March 15, 2024"
3. Verify edit is applied and highlighted
4. Check that changes are explained

### Test Scenario 3: Error Handling

1. Request an edit without a document
2. Provide incomplete information
3. Use ambiguous requests
4. Verify AI handles gracefully

## 🔒 Security Considerations

⚠️ **This is a demo application**. For production use:

- Add authentication and authorization
- Implement rate limiting
- Validate and sanitize all inputs
- Use environment variables for secrets
- Add HTTPS in production
- Implement proper error logging
- Add database for persistence
- Review generated documents with legal professionals

## 📝 API Documentation

### POST /chat

Endpoint for chat messages with SSE streaming.

**Request:**
```json
{
  "message": "User message",
  "conversation_id": "optional-uuid"
}
```

**Response:** SSE stream with events:
- `type: text` - Text chunk
- `type: function_call` - Function being called
- `type: document` - Generated/updated document
- `type: done` - Conversation complete
- `type: error` - Error occurred

### GET /conversations/:id

Get conversation history and current document.

### DELETE /conversations/:id

Delete conversation and associated data.

## 🎨 Design Philosophy

The application follows modern design principles:

- **Minimalism** - Clean interfaces without clutter
- **Feedback** - Visual indicators for all actions
- **Responsiveness** - Adapts to different screen sizes
- **Accessibility** - Semantic HTML and ARIA labels
- **Performance** - Optimized rendering and streaming

## 🚧 Future Enhancements

Potential improvements:

- [ ] Database integration for persistent storage
- [ ] User authentication and multi-user support
- [ ] Document versioning and history
- [ ] PDF export with formatting
- [ ] More document templates
- [ ] Advanced editing capabilities
- [ ] Document comparison tool
- [ ] Email/sharing functionality
- [ ] Template customization
- [ ] Multi-language support

## 🤝 Contributing

This is a technical challenge project. For production use cases:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Design inspiration from [transparently.ai](https://www.transparently.ai/)
- Built with [Next.js](https://nextjs.org/), [Flask](https://flask.palletsprojects.com/), and [Google Gemini](https://deepmind.google/technologies/gemini/)
- Icons by [Lucide](https://lucide.dev/)
- Animations by [Framer Motion](https://www.framer.com/motion/)

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Review the documentation
- Check the [PROMPT_ENGINEERING.md](./PROMPT_ENGINEERING.md) for prompt details

---

**Built with ❤️ for the Lexiden Tech Challenge**
