'use client'

import { useState, useRef } from 'react'
import ChatInterface from '@/components/ChatInterface'
import DocumentPreview from '@/components/DocumentPreview'
import { motion } from 'framer-motion'
import { FileText, MessageSquare, RotateCcw } from 'lucide-react'

export default function Home() {
  const [currentDocument, setCurrentDocument] = useState<string | null>(null)
  const [downloadDocument, setDownloadDocument] = useState<string | null>(null)
  const [documentChanges, setDocumentChanges] = useState<string | null>(null)
  const chatResetRef = useRef<(() => void) | null>(null)

  const handleDocumentUpdate = (doc: string | null, downloadDoc?: string | null) => {
    setCurrentDocument(doc)
    if (downloadDoc) {
      setDownloadDocument(downloadDoc)
    } else {
      setDownloadDocument(doc)
    }
  }

  const handleReset = () => {
    setCurrentDocument(null)
    setDownloadDocument(null)
    setDocumentChanges(null)
    chatResetRef.current?.()
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background-secondary to-accent-lightRed">
      {/* Header */}
      <motion.header
        className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50 shadow-soft"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-[90%] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-medium">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-text-primary">Legal Document Assistant</h1>
                <p className="text-sm text-text-secondary">AI-powered document generation</p>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-[90%] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
          {/* Chat Section */}
          <motion.div
            className="flex flex-col bg-white rounded-2xl shadow-medium overflow-hidden"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="bg-primary px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-5 h-5 text-white" />
                <h2 className="text-lg font-semibold text-white">Chat</h2>
              </div>
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-white/80 hover:text-white hover:bg-white/10 transition-colors"
                title="Clear chat and reset"
              >
                <RotateCcw className="w-4 h-4" />
                <span>New Chat</span>
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatInterface
                onDocumentUpdate={handleDocumentUpdate}
                onDocumentChanges={setDocumentChanges}
                onResetRef={(resetFn) => { chatResetRef.current = resetFn }}
              />
            </div>
          </motion.div>

          {/* Document Preview Section */}
          <motion.div
            className="flex flex-col bg-white rounded-2xl shadow-medium overflow-hidden"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <div className="bg-primary px-6 py-4 flex items-center gap-3">
              <FileText className="w-5 h-5 text-white" />
              <h2 className="text-lg font-semibold text-white">Document Preview</h2>
            </div>
            <div className="flex-1 overflow-hidden">
              <DocumentPreview
                document={currentDocument}
                documentDownload={downloadDocument}
                changes={documentChanges}
              />
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  )
}
