'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import Message from './Message'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

interface ChatInterfaceProps {
  onDocumentUpdate: (document: string | null) => void
  onDocumentChanges: (changes: string | null) => void
}

export default function ChatInterface({ onDocumentUpdate, onDocumentChanges }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your legal document assistant. I can help you create various legal documents like Director Appointment Resolutions, Non-Disclosure Agreements, or Employment Agreements. What would you like to create today?',
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Refs for batching streaming updates
  const streamingTextRef = useRef<string>('')
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const assistantMessageIdRef = useRef<string | null>(null)

  // Get API URL from environment variable
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Batched update function to prevent excessive re-renders
  const batchUpdateMessage = useCallback((messageId: string, content: string) => {
    // Clear any pending timeout
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current)
    }

    // Schedule update after a short delay to batch multiple chunks
    updateTimeoutRef.current = setTimeout(() => {
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? { ...msg, content }
            : msg
        )
      )
    }, 50) // 50ms debounce - batches multiple chunks together
  }, [])

  // Force immediate update (for completion)
  const forceUpdateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current)
      updateTimeoutRef.current = null
    }

    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId
          ? { ...msg, ...updates }
          : msg
      )
    )
  }, [])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Create assistant message placeholder
    const assistantMessageId = (Date.now() + 1).toString()
    assistantMessageIdRef.current = assistantMessageId

    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    }
    setMessages(prev => [...prev, assistantMessage])

    // Reset streaming text accumulator
    streamingTextRef.current = ''

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'text') {
                // Accumulate text in ref (doesn't trigger re-render)
                streamingTextRef.current += data.content

                // Batch update to state (debounced)
                batchUpdateMessage(assistantMessageId, streamingTextRef.current)

              } else if (data.type === 'document') {
                onDocumentUpdate(data.content)
                if (data.changes) {
                  onDocumentChanges(data.changes)
                }
              } else if (data.type === 'function_call') {
                // Show function call info
                const funcInfo = `\n\n_[Calling function: ${data.function}]_\n\n`
                streamingTextRef.current += funcInfo

                // Force immediate update for function calls
                forceUpdateMessage(assistantMessageId, { content: streamingTextRef.current })

              } else if (data.type === 'done') {
                // Force final update with complete content
                forceUpdateMessage(assistantMessageId, {
                  content: streamingTextRef.current,
                  isStreaming: false
                })

                if (!conversationId && data.conversation_id) {
                  setConversationId(data.conversation_id)
                }

              } else if (data.type === 'error') {
                streamingTextRef.current += `\n\nError: ${data.content}`

                // Force immediate update for errors
                forceUpdateMessage(assistantMessageId, {
                  content: streamingTextRef.current,
                  isStreaming: false
                })
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)

      // Clear any pending updates
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }

      forceUpdateMessage(assistantMessageId, {
        content: 'Sorry, there was an error processing your request. Please make sure the backend server is running.',
        isStreaming: false
      })
    } finally {
      setIsLoading(false)

      // Clean up refs
      streamingTextRef.current = ''
      assistantMessageIdRef.current = null
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message, index) => (
            <Message key={message.id} message={message} index={index} />
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here..."
            disabled={isLoading}
            rows={1}
            className={cn(
              "flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3",
              "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "bg-white text-text-primary placeholder:text-text-light",
              "min-h-[52px] max-h-32"
            )}
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className={cn(
              "px-6 py-3 rounded-xl font-medium",
              "bg-primary text-white",
              "hover:bg-primary-dark transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "flex items-center gap-2 shadow-medium"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-text-secondary mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
