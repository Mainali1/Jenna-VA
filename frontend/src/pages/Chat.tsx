import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PaperAirplaneIcon,
  MicrophoneIcon,
  StopIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  EllipsisVerticalIcon,
  PlusIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { useConversationStore } from '@store/conversationStore'
import { cn } from '@utils/cn'
import type { Message, Conversation } from '@/types'

interface ChatProps {
  className?: string
  isConnected?: boolean
  connectionType?: 'grpc' | 'websocket'
  isElectron?: boolean
  sendMessage?: (message: any) => void
}

interface MessageBubbleProps {
  message: Message
  isLast: boolean
  onSpeak: (text: string) => void
  onCopy: (text: string) => void
  onRegenerate?: () => void
}

interface VoiceVisualizerProps {
  isListening: boolean
  amplitude?: number
}

const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({ isListening, amplitude = 0.5 }) => {
  return (
    <div className="flex items-center justify-center space-x-1">
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          className="w-1 bg-red-500 rounded-full"
          animate={{
            height: isListening ? [4, 20, 4] : 4,
            opacity: isListening ? [0.4, 1, 0.4] : 0.4,
          }}
          transition={{
            duration: 0.8,
            repeat: isListening ? Infinity : 0,
            delay: i * 0.1,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isLast,
  onSpeak,
  onCopy,
  onRegenerate,
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  const handleSpeak = () => {
    if (isSpeaking) {
      // Stop speaking
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    } else {
      // Start speaking
      onSpeak(message.content)
      setIsSpeaking(true)
    }
  }

  const handleCopy = () => {
    onCopy(message.content)
  }

  // Format timestamp
  const formatTime = (timestamp: Date) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={cn(
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={cn(
        'max-w-[80%] group',
        isUser ? 'order-2' : 'order-1'
      )}>
        {/* Avatar */}
        <div className={cn(
          'flex items-end space-x-2',
          isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'
        )}>
          <div className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium',
            isUser ? 'bg-blue-500' : 'bg-purple-500'
          )}>
            {isUser ? 'U' : 'J'}
          </div>

          {/* Message Content */}
          <div className={cn(
            'relative px-4 py-3 rounded-2xl max-w-md',
            isUser
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-bl-md'
          )}>
            {/* Message Text */}
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>

            {/* Timestamp */}
            <div className={cn(
              'text-xs mt-2 opacity-70',
              isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
            )}>
              {formatTime(message.timestamp)}
            </div>

            {/* Message Actions */}
            <AnimatePresence>
              {(isHovered || isSpeaking) && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className={cn(
                    'absolute top-0 flex items-center space-x-1 p-1 rounded-lg shadow-lg',
                    'bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600',
                    isUser ? '-left-16' : '-right-16'
                  )}
                >
                  {/* Speak Button */}
                  <button
                    onClick={handleSpeak}
                    className={cn(
                      'p-1.5 rounded-md transition-colors duration-200',
                      'hover:bg-gray-100 dark:hover:bg-gray-600',
                      isSpeaking ? 'text-red-500' : 'text-gray-600 dark:text-gray-400'
                    )}
                    title={isSpeaking ? 'Stop speaking' : 'Speak message'}
                  >
                    {isSpeaking ? (
                      <SpeakerXMarkIcon className="w-4 h-4" />
                    ) : (
                      <SpeakerWaveIcon className="w-4 h-4" />
                    )}
                  </button>

                  {/* Copy Button */}
                  <button
                    onClick={handleCopy}
                    className="p-1.5 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                    title="Copy message"
                  >
                    <DocumentDuplicateIcon className="w-4 h-4" />
                  </button>

                  {/* Regenerate Button (for assistant messages) */}
                  {isAssistant && isLast && onRegenerate && (
                    <button
                      onClick={onRegenerate}
                      className="p-1.5 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                      title="Regenerate response"
                    >
                      <ArrowPathIcon className="w-4 h-4" />
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

const Chat: React.FC<ChatProps> = ({ 
  className, 
  isConnected, 
  connectionType, 
  isElectron,
  sendMessage: externalSendMessage 
}) => {
  const { isListening, startListening, stopListening } = useAppStore()
  const {
    currentConversation,
    isLoading,
    isTyping,
    sendMessage: internalSendMessage,
    createConversation,
    deleteConversation,
  } = useConversationStore()
  
  // Use external sendMessage if provided (from App), otherwise use internal
  const sendMessageFn = externalSendMessage || internalSendMessage

  const [inputValue, setInputValue] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentConversation?.messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Handle voice recording
  const handleVoiceToggle = () => {
    if (isListening || isRecording) {
      stopListening()
      setIsRecording(false)
    } else {
      startListening()
      setIsRecording(true)
    }
  }

  // Handle sending message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const message = inputValue.trim()
    setInputValue('')
    
    // If we're using external sendMessage (gRPC/WebSocket), send through that channel
    if (externalSendMessage && isConnected) {
      externalSendMessage({ type: 'chat_message', content: message })
    }

    // Only use internal sendMessage if external is not available
    if (!externalSendMessage || !isConnected) {
      if (!currentConversation) {
        await createConversation(message)
      } else {
        await internalSendMessage(message)
      }
    }
  }

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Handle speaking message
  const handleSpeak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.pitch = 1
      utterance.volume = 0.8
      window.speechSynthesis.speak(utterance)
    }
  }

  // Handle copying message
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    // You could add a toast notification here
  }

  // Handle regenerating response
  const handleRegenerate = () => {
    if (currentConversation?.messages.length) {
      const lastUserMessage = [...currentConversation.messages]
        .reverse()
        .find(m => m.role === 'user')
      
      if (lastUserMessage) {
        sendMessage(lastUserMessage.content, true) // true for regenerate
      }
    }
  }

  // Handle new conversation
  const handleNewConversation = () => {
    createConversation('New Chat')
  }

  // Handle clear conversation
  const handleClearConversation = () => {
    if (currentConversation && window.confirm('Are you sure you want to clear this conversation?')) {
      deleteConversation(currentConversation.id)
    }
  }

  const messages = currentConversation?.messages || []

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-3">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            {currentConversation?.title || 'New Chat'}
          </h1>
          {messages.length > 0 && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {messages.length} messages
            </span>
          )}
          
          {/* Connection status indicator */}
          {isElectron && (
            <div className="flex items-center ml-2">
              <span 
                className={cn(
                  "inline-block w-2 h-2 rounded-full mr-1",
                  isConnected ? "bg-green-500" : "bg-red-500"
                )}
              />
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {connectionType?.toUpperCase()}
                {isElectron && " [Electron]"}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleNewConversation}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
            title="New conversation"
          >
            <PlusIcon className="w-5 h-5" />
          </button>
          
          {messages.length > 0 && (
            <button
              onClick={handleClearConversation}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
              title="Clear conversation"
            >
              <TrashIcon className="w-5 h-5" />
            </button>
          )}
          
          <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200">
            <EllipsisVerticalIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center mb-4">
              <MicrophoneIcon className="w-8 h-8 text-purple-500" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md">
              Ask me anything! I can help you with tasks, answer questions, or just have a friendly chat.
            </p>
            <div className="flex items-center space-x-4 mt-6">
              <button
                onClick={() => setInputValue('What can you help me with?')}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200"
              >
                Get started
              </button>
              <button
                onClick={handleVoiceToggle}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
              >
                Use voice
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={message.id}
                message={message}
                isLast={index === messages.length - 1}
                onSpeak={handleSpeak}
                onCopy={handleCopy}
                onRegenerate={message.role === 'assistant' ? handleRegenerate : undefined}
              />
            ))}
            
            {/* Typing Indicator */}
            <AnimatePresence>
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex justify-start"
                >
                  <div className="flex items-end space-x-2">
                    <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm font-medium">
                      J
                    </div>
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
                      <div className="flex space-x-1">
                        {[...Array(3)].map((_, i) => (
                          <motion.div
                            key={i}
                            className="w-2 h-2 bg-gray-400 rounded-full"
                            animate={{ opacity: [0.4, 1, 0.4] }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              delay: i * 0.2,
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        {/* Voice Recording Indicator */}
        <AnimatePresence>
          {(isListening || isRecording) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-red-700 dark:text-red-400 font-medium">
                    Listening...
                  </span>
                  <VoiceVisualizer isListening={isListening || isRecording} />
                </div>
                <button
                  onClick={handleVoiceToggle}
                  className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                >
                  <StopIcon className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input Form */}
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message or use voice..."
              className={cn(
                'w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 dark:border-gray-600',
                'bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
                'placeholder-gray-500 dark:placeholder-gray-400',
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'resize-none max-h-32 min-h-[48px]',
                'transition-colors duration-200'
              )}
              rows={1}
              disabled={isLoading}
            />
            
            {/* Voice Button */}
            <button
              onClick={handleVoiceToggle}
              className={cn(
                'absolute right-3 bottom-3 p-2 rounded-lg transition-colors duration-200',
                (isListening || isRecording)
                  ? 'text-red-500 hover:text-red-600 bg-red-50 dark:bg-red-900/20'
                  : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
              )}
              title={isListening || isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {isListening || isRecording ? (
                <StopIcon className="w-5 h-5" />
              ) : (
                <MicrophoneIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          
          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className={cn(
              'p-3 rounded-xl transition-colors duration-200',
              inputValue.trim() && !isLoading
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
            )}
            title="Send message"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Input Help Text */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>{inputValue.length}/2000</span>
        </div>
      </div>
    </div>
  )
}

export default Chat