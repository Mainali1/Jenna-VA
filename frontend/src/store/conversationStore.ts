import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Conversation, Message, ConversationStore } from '@/types'
import { ApiClient } from '@/utils/api'

interface ConversationState {
  // State
  conversations: Conversation[]
  currentConversation: Conversation | null
  isLoading: boolean
  isTyping: boolean
  error: string | null
  searchQuery: string
  filteredConversations: Conversation[]
  
  // Actions
  loadConversations: () => Promise<void>
  createConversation: (title?: string) => Promise<Conversation | null>
  selectConversation: (id: string) => Promise<void>
  sendMessage: (content: string, type?: 'text' | 'voice') => Promise<Message | null>
  deleteConversation: (id: string) => Promise<void>
  clearCurrentConversation: () => void
  setTyping: (typing: boolean) => void
  setError: (error: string | null) => void
  searchConversations: (query: string) => void
  clearSearch: () => void
  updateConversationTitle: (id: string, title: string) => Promise<void>
  markAsRead: (conversationId: string) => void
  exportConversation: (id: string) => Promise<string | null>
  importConversation: (data: string) => Promise<Conversation | null>
  getConversationStats: () => {
    total: number
    today: number
    thisWeek: number
    totalMessages: number
  }
  cleanup: () => void
}

const useConversationStore = create<ConversationState>()()
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        conversations: [],
        currentConversation: null,
        isLoading: false,
        isTyping: false,
        error: null,
        searchQuery: '',
        filteredConversations: [],

        // Load all conversations
        loadConversations: async () => {
          set({ isLoading: true, error: null })
          
          try {
            const response = await ApiClient.getConversations()
            
            if (response.success && response.data) {
              const conversations = response.data.sort(
                (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
              )
              
              set({ 
                conversations,
                filteredConversations: conversations,
                isLoading: false 
              })
            } else {
              throw new Error(response.message || 'Failed to load conversations')
            }
          } catch (error) {
            console.error('Failed to load conversations:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to load conversations',
              isLoading: false 
            })
          }
        },

        // Create a new conversation
        createConversation: async (title?: string) => {
          set({ isLoading: true, error: null })
          
          try {
            const response = await ApiClient.createConversation(title)
            
            if (response.success && response.data) {
              const newConversation = response.data
              const { conversations } = get()
              const updatedConversations = [newConversation, ...conversations]
              
              set({ 
                conversations: updatedConversations,
                filteredConversations: updatedConversations,
                currentConversation: newConversation,
                isLoading: false 
              })
              
              return newConversation
            } else {
              throw new Error(response.message || 'Failed to create conversation')
            }
          } catch (error) {
            console.error('Failed to create conversation:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to create conversation',
              isLoading: false 
            })
            return null
          }
        },

        // Select and load a conversation
        selectConversation: async (id: string) => {
          set({ isLoading: true, error: null })
          
          try {
            // First check if conversation is already loaded
            const { conversations } = get()
            const existingConversation = conversations.find(c => c.id === id)
            
            if (existingConversation && existingConversation.messages.length > 0) {
              set({ 
                currentConversation: existingConversation,
                isLoading: false 
              })
              return
            }
            
            // Load conversation from API
            const response = await ApiClient.getConversation(id)
            
            if (response.success && response.data) {
              const conversation = response.data
              
              // Update conversations list with loaded conversation
              const updatedConversations = conversations.map(c => 
                c.id === id ? conversation : c
              )
              
              set({ 
                conversations: updatedConversations,
                filteredConversations: updatedConversations,
                currentConversation: conversation,
                isLoading: false 
              })
            } else {
              throw new Error(response.message || 'Failed to load conversation')
            }
          } catch (error) {
            console.error('Failed to select conversation:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to load conversation',
              isLoading: false 
            })
          }
        },

        // Send a message
        sendMessage: async (content: string, type: 'text' | 'voice' = 'text') => {
          const { currentConversation } = get()
          
          if (!currentConversation) {
            set({ error: 'No conversation selected' })
            return null
          }
          
          set({ isTyping: true, error: null })
          
          try {
            const response = await ApiClient.sendMessage(currentConversation.id, content, type)
            
            if (response.success && response.data) {
              const newMessage = response.data
              
              // Update current conversation with new message
              const updatedConversation = {
                ...currentConversation,
                messages: [...currentConversation.messages, newMessage],
                updated_at: new Date().toISOString(),
              }
              
              // Update conversations list
              const { conversations } = get()
              const updatedConversations = conversations.map((c: Conversation) => 
                c.id === currentConversation.id ? updatedConversation : c
              ).sort((a: Conversation, b: Conversation) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
              
              set({ 
                conversations: updatedConversations,
                filteredConversations: updatedConversations,
                currentConversation: updatedConversation,
                isTyping: false 
              })
              
              return newMessage
            } else {
              const errorMsg = 'message' in response ? response.message : 'Failed to send message';
              throw new Error(errorMsg)
            }
          } catch (error) {
            console.error('Failed to send message:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to send message',
              isTyping: false 
            })
            return null
          }
        },

        // Delete a conversation
        deleteConversation: async (id: string) => {
          set({ isLoading: true, error: null })
          
          try {
            const response = await ApiClient.deleteConversation(id)
            
            if (response.success) {
              const { conversations, currentConversation } = get() as ConversationState;
              const updatedConversations = conversations.filter((c: Conversation) => c.id !== id)
              
              set({ 
                conversations: updatedConversations,
                filteredConversations: updatedConversations,
                currentConversation: currentConversation?.id === id ? null : currentConversation,
                isLoading: false 
              })
            } else {
              const errorMsg = 'message' in response ? response.message : 'Failed to delete conversation';
              throw new Error(errorMsg)
            }
          } catch (error) {
            console.error('Failed to delete conversation:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to delete conversation',
              isLoading: false 
            })
          }
        },

        // Clear current conversation
        clearCurrentConversation: () => {
          set({ currentConversation: null })
        },

        // Set typing indicator
        setTyping: (typing: boolean) => {
          set({ isTyping: typing })
        },

        // Set error state
        setError: (error: string | null) => {
          set({ error })
        },

        // Search conversations
        searchConversations: (query: string) => {
          const { conversations } = get() as ConversationState;
          
          if (!query.trim()) {
            set({ 
              searchQuery: '',
              filteredConversations: conversations 
            })
            return
          }
          
          const filtered = conversations.filter(conversation => {
            const titleMatch = conversation.title.toLowerCase().includes(query.toLowerCase())
            const messageMatch = conversation.messages.some(message => 
              message.content.toLowerCase().includes(query.toLowerCase())
            )
            return titleMatch || messageMatch
          })
          
          set({ 
            searchQuery: query,
            filteredConversations: filtered 
          })
        },

        // Clear search
        clearSearch: () => {
          const { conversations } = get()
          set({ 
            searchQuery: '',
            filteredConversations: conversations 
          })
        },

        // Update conversation title
        updateConversationTitle: async (id: string, title: string) => {
          try {
            // Optimistically update UI
            const { conversations, currentConversation } = get()
            const updatedConversations = conversations.map(c => 
              c.id === id ? { ...c, title } : c
            )
            
            set({ 
              conversations: updatedConversations,
              filteredConversations: updatedConversations,
              currentConversation: currentConversation?.id === id 
                ? { ...currentConversation, title }
                : currentConversation
            })
            
            // TODO: Add API call to update title on server
            // await ApiClient.updateConversationTitle(id, title)
          } catch (error) {
            console.error('Failed to update conversation title:', error)
            set({ error: 'Failed to update conversation title' })
          }
        },

        // Mark conversation as read
        markAsRead: (conversationId: string) => {
          const { conversations } = get()
          const updatedConversations = conversations.map(c => 
            c.id === conversationId ? { ...c, unread_count: 0 } : c
          )
          
          set({ 
            conversations: updatedConversations,
            filteredConversations: updatedConversations
          })
        },

        // Export conversation
        exportConversation: async (id: string) => {
          try {
            const { conversations } = get()
            const conversation = conversations.find(c => c.id === id)
            
            if (!conversation) {
              throw new Error('Conversation not found')
            }
            
            const exportData = {
              title: conversation.title,
              created_at: conversation.created_at,
              messages: conversation.messages.map(m => ({
                role: m.role,
                content: m.content,
                timestamp: m.timestamp,
              })),
              exported_at: new Date().toISOString(),
            }
            
            return JSON.stringify(exportData, null, 2)
          } catch (error) {
            console.error('Failed to export conversation:', error)
            set({ error: 'Failed to export conversation' })
            return null
          }
        },

        // Import conversation
        importConversation: async (data: string) => {
          try {
            const importData = JSON.parse(data)
            
            // Validate import data structure
            if (!importData.title || !importData.messages || !Array.isArray(importData.messages)) {
              throw new Error('Invalid conversation data format')
            }
            
            // Create new conversation with imported data
            const newConversation = await get().createConversation(importData.title)
            
            if (newConversation) {
              // TODO: Add API call to import messages
              // For now, just update the local state
              const { conversations } = get()
              const updatedConversation = {
                ...newConversation,
                messages: importData.messages.map((m: any, index: number) => ({
                  id: `imported_${Date.now()}_${index}`,
                  conversation_id: newConversation.id,
                  role: m.role,
                  content: m.content,
                  timestamp: m.timestamp || new Date().toISOString(),
                  type: 'text',
                })),
              }
              
              const updatedConversations = conversations.map(c => 
                c.id === newConversation.id ? updatedConversation : c
              )
              
              set({ 
                conversations: updatedConversations,
                filteredConversations: updatedConversations,
                currentConversation: updatedConversation
              })
              
              return updatedConversation
            }
            
            return null
          } catch (error) {
            console.error('Failed to import conversation:', error)
            set({ error: 'Failed to import conversation' })
            return null
          }
        },

        // Get conversation statistics
        getConversationStats: () => {
          const { conversations } = get()
          const now = new Date()
          const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
          
          const todayConversations = conversations.filter(c => 
            new Date(c.created_at) >= today
          ).length
          
          const weekConversations = conversations.filter(c => 
            new Date(c.created_at) >= weekAgo
          ).length
          
          const totalMessages = conversations.reduce((total, c) => 
            total + c.messages.length, 0
          )
          
          return {
            total: conversations.length,
            today: todayConversations,
            thisWeek: weekConversations,
            totalMessages,
          }
        },

        // Cleanup function
        cleanup: () => {
          set({ 
            currentConversation: null,
            isLoading: false,
            isTyping: false,
            error: null,
            searchQuery: '',
          })
        },
      }),
      {
        name: 'jenna-conversation-store',
        partialize: (state) => ({
          conversations: state.conversations,
          // Don't persist current conversation, loading states, or errors
        }),
      }
    ),
    {
      name: 'conversation-store',
    }
  )

// Utility hooks for specific conversation operations
export const useCurrentConversation = () => {
  return useConversationStore(state => state.currentConversation)
}

export const useConversationList = () => {
  return useConversationStore(state => ({
    conversations: state.filteredConversations,
    isLoading: state.isLoading,
    searchQuery: state.searchQuery,
    searchConversations: state.searchConversations,
    clearSearch: state.clearSearch,
  }))
}

export const useConversationActions = () => {
  return useConversationStore(state => ({
    createConversation: state.createConversation,
    selectConversation: state.selectConversation,
    sendMessage: state.sendMessage,
    deleteConversation: state.deleteConversation,
    updateConversationTitle: state.updateConversationTitle,
    markAsRead: state.markAsRead,
    exportConversation: state.exportConversation,
    importConversation: state.importConversation,
  }))
}

export const useConversationStatus = () => {
  return useConversationStore(state => ({
    isLoading: state.isLoading,
    isTyping: state.isTyping,
    error: state.error,
    setError: state.setError,
  }))
}

export default useConversationStore