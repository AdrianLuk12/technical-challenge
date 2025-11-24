# Legal Document Assistant - Frontend

Next.js frontend with SSE streaming client and real-time document preview.

## Tech Stack

- **Framework**: Next.js 15.1.3 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Build Tool**: Turbopack

## Features

- Real-time SSE streaming chat interface
- Live document preview with syntax highlighting
- Edit change notifications
- Responsive design (mobile-friendly)
- Smooth animations and transitions
- Download generated documents

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env.local` file:
   ```bash
   cp .env.local.example .env.local
   ```

3. Configure environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

   **Important:** Change the URL if your backend runs on a different port or host.

4. Start development server:
   ```bash
   npm run dev
   ```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL (default: `http://localhost:5000`)
  - Used for all API requests (/chat, /conversations, etc.)
  - Must be prefixed with `NEXT_PUBLIC_` to be accessible in browser
  - Can be changed for production deployment

## Project Structure

```
src/
├── app/
│   ├── layout.tsx      # Root layout with metadata
│   ├── page.tsx        # Home page with chat + preview
│   └── globals.css     # Global styles and Tailwind
├── components/
│   ├── ChatInterface.tsx       # Main chat component
│   ├── Message.tsx            # Individual message
│   └── DocumentPreview.tsx    # Document display
└── lib/
    └── utils.ts        # Utility functions (cn, etc.)
```

## Components

### ChatInterface

Main chat component handling:
- Message history
- SSE streaming connection
- User input and sending
- Function call visualization

### Message

Individual message component with:
- User/Assistant avatars
- Timestamps
- Streaming indicators
- Markdown support

### DocumentPreview

Document display component featuring:
- Live preview updates
- Download functionality
- Edit change notifications
- Syntax highlighting

## Styling

The app uses a custom Tailwind theme inspired by transparently.ai:

- **Primary Colors**: Light Red, Red, Deep Red
- **Typography**: Inter font
- **Spacing**: Generous whitespace
- **Borders**: Rounded xl corners
- **Shadows**: Soft, subtle shadows

## API Integration

The frontend connects to the Flask backend at `http://localhost:5000`:

- `POST /chat` - Send messages and receive SSE stream
- `GET /conversations/:id` - Get conversation history
- `DELETE /conversations/:id` - Clear conversation

## Development

### Commands

- `npm run dev` - Start development server (Turbopack)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding New Document Types

1. Backend: Add template function in `backend/app.py`
2. Update system prompt with new document requirements
3. Frontend: No changes needed (automatically supports new types)

## Performance

- Uses Turbopack for faster development builds
- Components are optimized with React.memo where appropriate
- SSE streaming prevents UI blocking
- Framer Motion uses GPU-accelerated transforms

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## Troubleshooting

### SSE Connection Issues

If streaming doesn't work:
1. Check backend is running on port 5000
2. Verify CORS is enabled in Flask
3. Check browser console for errors

### Styling Issues

If styles don't load:
1. Ensure Tailwind is configured correctly
2. Run `npm install` to ensure dependencies
3. Clear `.next` cache and rebuild

### Build Errors

If build fails:
1. Check TypeScript errors: `npm run lint`
2. Verify all dependencies are installed
3. Ensure Node.js version is 18+

## Future Enhancements

- [ ] Markdown rendering in messages
- [ ] Code syntax highlighting in documents
- [ ] Document comparison view
- [ ] Print-friendly document view
- [ ] Dark mode support
- [ ] Keyboard shortcuts
- [ ] Voice input support
