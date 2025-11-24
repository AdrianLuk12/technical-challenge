'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Download, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DocumentPreviewProps {
  document: string | null
  changes: string | null
}

export default function DocumentPreview({ document, changes }: DocumentPreviewProps) {
  const [highlightedDocument, setHighlightedDocument] = useState<string | null>(null)
  const [showChanges, setShowChanges] = useState(false)

  useEffect(() => {
    if (document) {
      setHighlightedDocument(document)

      // Show changes notification if there are changes
      if (changes) {
        setShowChanges(true)
        const timeoutId = setTimeout(() => setShowChanges(false), 3000)
        return () => clearTimeout(timeoutId)
      }
    }
  }, [document, changes])

  const handleDownload = () => {
    if (!document) return

    const blob = new Blob([document], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement('a')
    a.href = url
    a.download = 'legal-document.txt'
    window.document.body.appendChild(a)
    a.click()
    window.document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!document) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col items-center"
        >
          <div className="w-24 h-24 bg-gray-100 rounded-2xl flex items-center justify-center mb-4 mx-auto">
            <FileText className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-text-primary mb-2">
            No Document Yet
          </h3>
          <p className="text-sm text-text-secondary max-w-xs mx-auto">
            Start a conversation to generate your legal document. The document will appear here as it&apos;s created.
          </p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Document Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary" />
          <span className="font-medium text-text-primary">Generated Document</span>
        </div>
        <button
          onClick={handleDownload}
          className={cn(
            "px-4 py-2 rounded-lg font-medium text-sm",
            "bg-primary text-white",
            "hover:bg-primary-dark transition-colors",
            "flex items-center gap-2 shadow-soft"
          )}
        >
          <Download className="w-4 h-4" />
          Download
        </button>
      </div>

      {/* Changes Notification */}
      <AnimatePresence>
        {showChanges && changes && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="m-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2"
          >
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-800">Document Updated</p>
              <p className="text-xs text-yellow-700 mt-1">{changes}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document Content */}
      <motion.div
        className="flex-1 overflow-y-auto p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="document-preview bg-white rounded-lg p-6 shadow-soft border border-gray-200">
          <pre className="whitespace-pre-wrap font-mono text-sm text-text-primary leading-relaxed">
            {highlightedDocument}
          </pre>
        </div>
      </motion.div>
    </div>
  )
}
