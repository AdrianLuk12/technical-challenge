'use client'

import { motion } from 'framer-motion'
import { User, Bot, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'
import { formatTimestamp } from '@/lib/utils'

interface MessageProps {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
    isStreaming?: boolean
  }
  index: number
}

export default function Message({ message, index }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={cn(
        "flex gap-3 p-4 rounded-xl",
        isUser ? "bg-primary/5 ml-8" : "bg-gray-50 mr-8"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-primary" : "bg-accent-red"
        )}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm text-text-primary">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className="text-xs text-text-light">
            {formatTimestamp(message.timestamp)}
          </span>
          {message.isStreaming && (
            <Loader2 className="w-3 h-3 text-primary animate-spin" />
          )}
        </div>

        {/* Message content with markdown support for assistant */}
        {isUser ? (
          // User messages: plain text with line breaks
          <div className="text-text-primary whitespace-pre-wrap break-words">
            {message.content}
          </div>
        ) : (
          // Assistant messages: render markdown
          <div className="text-text-primary prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Style code blocks
                code: ({ node, inline, className, children, ...props }) => (
                  inline ? (
                    <code
                      className="bg-gray-200 text-primary px-1 py-0.5 rounded text-sm font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  ) : (
                    <code
                      className="block bg-gray-100 p-3 rounded-lg overflow-x-auto text-sm font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  )
                ),
                // Style links
                a: ({ node, children, ...props }) => (
                  <a
                    className="text-primary hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                    {...props}
                  >
                    {children}
                  </a>
                ),
                // Style lists
                ul: ({ node, children, ...props }) => (
                  <ul className="list-disc list-inside space-y-1 my-2" {...props}>
                    {children}
                  </ul>
                ),
                ol: ({ node, children, ...props }) => (
                  <ol className="list-decimal list-inside space-y-1 my-2" {...props}>
                    {children}
                  </ol>
                ),
                // Style paragraphs
                p: ({ node, children, ...props }) => (
                  <p className="my-2 leading-relaxed" {...props}>
                    {children}
                  </p>
                ),
                // Style headers
                h1: ({ node, children, ...props }) => (
                  <h1 className="text-xl font-bold mt-4 mb-2" {...props}>
                    {children}
                  </h1>
                ),
                h2: ({ node, children, ...props }) => (
                  <h2 className="text-lg font-bold mt-3 mb-2" {...props}>
                    {children}
                  </h2>
                ),
                h3: ({ node, children, ...props }) => (
                  <h3 className="text-base font-semibold mt-2 mb-1" {...props}>
                    {children}
                  </h3>
                ),
                // Style blockquotes
                blockquote: ({ node, children, ...props }) => (
                  <blockquote
                    className="border-l-4 border-primary pl-4 my-2 italic text-gray-700"
                    {...props}
                  >
                    {children}
                  </blockquote>
                ),
                // Style tables
                table: ({ node, children, ...props }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="min-w-full border-collapse border border-gray-300" {...props}>
                      {children}
                    </table>
                  </div>
                ),
                th: ({ node, children, ...props }) => (
                  <th className="border border-gray-300 px-4 py-2 bg-gray-100 font-semibold" {...props}>
                    {children}
                  </th>
                ),
                td: ({ node, children, ...props }) => (
                  <td className="border border-gray-300 px-4 py-2" {...props}>
                    {children}
                  </td>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>

            {/* Streaming indicator when no content yet */}
            {message.isStreaming && !message.content && (
              <span className="inline-flex gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}
