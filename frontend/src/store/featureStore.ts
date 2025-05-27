import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { FeatureDefinition, FeatureStore } from '@/types'
import { ApiClient } from '@/utils/api'

interface FeatureState {
  // State
  features: FeatureDefinition[]
  isLoading: boolean
  error: string | null
  searchQuery: string
  filteredFeatures: FeatureDefinition[]
  selectedCategory: string | null
  
  // Actions
  loadFeatures: () => Promise<void>
  toggleFeature: (id: string, enabled: boolean) => Promise<void>
  updateFeatureSettings: (id: string, settings: any) => Promise<void>
  getFeature: (id: string) => FeatureDefinition | undefined
  searchFeatures: (query: string) => void
  filterByCategory: (category: string | null) => void
  clearFilters: () => void
  setError: (error: string | null) => void
  getEnabledFeatures: () => FeatureDefinition[]
  getFeaturesByCategory: (category: string) => FeatureDefinition[]
  getFeatureStats: () => {
    total: number
    enabled: number
    disabled: number
    byCategory: Record<string, number>
  }
  resetFeatureToDefaults: (id: string) => Promise<void>
  exportFeatureSettings: () => string
  importFeatureSettings: (data: string) => Promise<void>
  cleanup: () => void
}

const useFeatureStore = create<FeatureState>()()
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        features: [],
        isLoading: false,
        error: null,
        searchQuery: '',
        filteredFeatures: [],
        selectedCategory: null,

        // Load all features
        loadFeatures: async () => {
          set({ isLoading: true, error: null })
          
          try {
            const response = await ApiClient.getFeatures()
            
            if (response.success && response.data) {
              const features = response.data.sort((a, b) => a.name.localeCompare(b.name))
              
              set({ 
                features,
                filteredFeatures: features,
                isLoading: false 
              })
            } else {
              throw new Error(response.message || 'Failed to load features')
            }
          } catch (error) {
            console.error('Failed to load features:', error)
            set({ 
              error: error instanceof Error ? error.message : 'Failed to load features',
              isLoading: false 
            })
          }
        },

        // Toggle feature on/off
        toggleFeature: async (id: string, enabled: boolean) => {
          const { features } = get()
          const feature = features.find(f => f.id === id)
          
          if (!feature) {
            set({ error: 'Feature not found' })
            return
          }
          
          // Optimistically update UI
          const updatedFeatures = features.map(f => 
            f.id === id ? { ...f, enabled } : f
          )
          
          set({ 
            features: updatedFeatures,
            filteredFeatures: get().applyFilters(updatedFeatures)
          })
          
          try {
            const response = await ApiClient.toggleFeature(id, enabled)
            
            if (response.success && response.data) {
              // Update with server response
              const serverFeature = response.data
              const finalFeatures = features.map(f => 
                f.id === id ? serverFeature : f
              )
              
              set({ 
                features: finalFeatures,
                filteredFeatures: get().applyFilters(finalFeatures),
                error: null
              })
            } else {
              throw new Error(response.message || 'Failed to toggle feature')
            }
          } catch (error) {
            console.error('Failed to toggle feature:', error)
            
            // Revert optimistic update
            const revertedFeatures = features.map(f => 
              f.id === id ? feature : f
            )
            
            set({ 
              features: revertedFeatures,
              filteredFeatures: get().applyFilters(revertedFeatures),
              error: error instanceof Error ? error.message : 'Failed to toggle feature'
            })
          }
        },

        // Update feature settings
        updateFeatureSettings: async (id: string, settings: any) => {
          const { features } = get()
          const feature = features.find(f => f.id === id)
          
          if (!feature) {
            set({ error: 'Feature not found' })
            return
          }
          
          // Optimistically update UI
          const updatedFeatures = features.map(f => 
            f.id === id ? { ...f, settings: { ...f.settings, ...settings } } : f
          )
          
          set({ 
            features: updatedFeatures,
            filteredFeatures: get().applyFilters(updatedFeatures)
          })
          
          try {
            const response = await ApiClient.updateFeatureSettings(id, settings)
            
            if (response.success && response.data) {
              // Update with server response
              const serverFeature = response.data
              const finalFeatures = features.map(f => 
                f.id === id ? serverFeature : f
              )
              
              set({ 
                features: finalFeatures,
                filteredFeatures: get().applyFilters(finalFeatures),
                error: null
              })
            } else {
              throw new Error(response.message || 'Failed to update feature settings')
            }
          } catch (error) {
            console.error('Failed to update feature settings:', error)
            
            // Revert optimistic update
            const revertedFeatures = features.map(f => 
              f.id === id ? feature : f
            )
            
            set({ 
              features: revertedFeatures,
              filteredFeatures: get().applyFilters(revertedFeatures),
              error: error instanceof Error ? error.message : 'Failed to update feature settings'
            })
          }
        },

        // Get a specific feature
        getFeature: (id: string) => {
          const { features } = get()
          return features.find(f => f.id === id)
        },

        // Search features
        searchFeatures: (query: string) => {
          const { features, selectedCategory } = get()
          set({ searchQuery: query })
          
          let filtered = features
          
          // Apply category filter
          if (selectedCategory) {
            filtered = filtered.filter(f => f.category === selectedCategory)
          }
          
          // Apply search filter
          if (query.trim()) {
            const searchTerm = query.toLowerCase()
            filtered = filtered.filter(f => 
              f.name.toLowerCase().includes(searchTerm) ||
              f.description.toLowerCase().includes(searchTerm) ||
              f.category.toLowerCase().includes(searchTerm)
            )
          }
          
          set({ filteredFeatures: filtered })
        },

        // Filter by category
        filterByCategory: (category: string | null) => {
          set({ selectedCategory: category })
          get().applyFilters()
        },

        // Clear all filters
        clearFilters: () => {
          const { features } = get()
          set({ 
            searchQuery: '',
            selectedCategory: null,
            filteredFeatures: features
          })
        },

        // Apply current filters (internal helper)
        applyFilters: (featureList?: FeatureDefinition[]) => {
          const { features, searchQuery, selectedCategory } = get()
          const targetFeatures = featureList || features
          
          let filtered = targetFeatures
          
          // Apply category filter
          if (selectedCategory) {
            filtered = filtered.filter(f => f.category === selectedCategory)
          }
          
          // Apply search filter
          if (searchQuery.trim()) {
            const searchTerm = searchQuery.toLowerCase()
            filtered = filtered.filter(f => 
              f.name.toLowerCase().includes(searchTerm) ||
              f.description.toLowerCase().includes(searchTerm) ||
              f.category.toLowerCase().includes(searchTerm)
            )
          }
          
          if (!featureList) {
            set({ filteredFeatures: filtered })
          }
          
          return filtered
        },

        // Set error state
        setError: (error: string | null) => {
          set({ error })
        },

        // Get enabled features
        getEnabledFeatures: () => {
          const { features } = get()
          return features.filter(f => f.enabled)
        },

        // Get features by category
        getFeaturesByCategory: (category: string) => {
          const { features } = get()
          return features.filter(f => f.category === category)
        },

        // Get feature statistics
        getFeatureStats: () => {
          const { features } = get()
          
          const enabled = features.filter(f => f.enabled).length
          const disabled = features.length - enabled
          
          const byCategory = features.reduce((acc, feature) => {
            acc[feature.category] = (acc[feature.category] || 0) + 1
            return acc
          }, {} as Record<string, number>)
          
          return {
            total: features.length,
            enabled,
            disabled,
            byCategory,
          }
        },

        // Reset feature to default settings
        resetFeatureToDefaults: async (id: string) => {
          const { features } = get()
          const feature = features.find(f => f.id === id)
          
          if (!feature) {
            set({ error: 'Feature not found' })
            return
          }
          
          try {
            // Reset to default settings (assuming API supports this)
            await get().updateFeatureSettings(id, feature.defaultSettings || {})
          } catch (error) {
            console.error('Failed to reset feature to defaults:', error)
            set({ error: 'Failed to reset feature to defaults' })
          }
        },

        // Export feature settings
        exportFeatureSettings: () => {
          const { features } = get()
          
          const exportData = {
            version: '1.0',
            exported_at: new Date().toISOString(),
            features: features.map(f => ({
              id: f.id,
              enabled: f.enabled,
              settings: f.settings,
            })),
          }
          
          return JSON.stringify(exportData, null, 2)
        },

        // Import feature settings
        importFeatureSettings: async (data: string) => {
          try {
            const importData = JSON.parse(data)
            
            // Validate import data structure
            if (!importData.features || !Array.isArray(importData.features)) {
              throw new Error('Invalid feature settings data format')
            }
            
            const { features } = get()
            
            // Apply imported settings
            for (const importedFeature of importData.features) {
              const existingFeature = features.find(f => f.id === importedFeature.id)
              
              if (existingFeature) {
                // Update feature state
                if (typeof importedFeature.enabled === 'boolean') {
                  await get().toggleFeature(importedFeature.id, importedFeature.enabled)
                }
                
                // Update feature settings
                if (importedFeature.settings) {
                  await get().updateFeatureSettings(importedFeature.id, importedFeature.settings)
                }
              }
            }
            
            set({ error: null })
          } catch (error) {
            console.error('Failed to import feature settings:', error)
            set({ error: 'Failed to import feature settings' })
          }
        },

        // Cleanup function
        cleanup: () => {
          set({ 
            isLoading: false,
            error: null,
            searchQuery: '',
            selectedCategory: null,
          })
        },
      }),
      {
        name: 'jenna-feature-store',
        partialize: (state) => ({
          features: state.features,
          // Don't persist loading states, errors, or filters
        }),
      }
    ),
    {
      name: 'feature-store',
    }
  )

// Utility hooks for specific feature operations
export const useFeatureList = () => {
  return useFeatureStore(state => ({
    features: state.filteredFeatures,
    isLoading: state.isLoading,
    searchQuery: state.searchQuery,
    selectedCategory: state.selectedCategory,
    searchFeatures: state.searchFeatures,
    filterByCategory: state.filterByCategory,
    clearFilters: state.clearFilters,
  }))
}

export const useFeatureActions = () => {
  return useFeatureStore(state => ({
    toggleFeature: state.toggleFeature,
    updateFeatureSettings: state.updateFeatureSettings,
    resetFeatureToDefaults: state.resetFeatureToDefaults,
    exportFeatureSettings: state.exportFeatureSettings,
    importFeatureSettings: state.importFeatureSettings,
  }))
}

export const useFeatureStatus = () => {
  return useFeatureStore(state => ({
    isLoading: state.isLoading,
    error: state.error,
    setError: state.setError,
  }))
}

export const useFeatureStats = () => {
  return useFeatureStore(state => state.getFeatureStats())
}

export const useEnabledFeatures = () => {
  return useFeatureStore(state => state.getEnabledFeatures())
}

export const useFeaturesByCategory = (category: string) => {
  return useFeatureStore(state => state.getFeaturesByCategory(category))
}

export const useFeature = (id: string) => {
  return useFeatureStore(state => state.getFeature(id))
}

// Feature categories helper
export const getFeatureCategories = (features: FeatureDefinition[]): string[] => {
  const categories = new Set(features.map(f => f.category))
  return Array.from(categories).sort()
}

// Feature validation helpers
export const validateFeatureSettings = (feature: FeatureDefinition, settings: any): boolean => {
  if (!feature.settingsSchema) return true
  
  // Basic validation - in a real app, you'd use a proper schema validator
  try {
    const schema = feature.settingsSchema
    
    for (const [key, value] of Object.entries(settings)) {
      const fieldSchema = schema[key]
      if (!fieldSchema) continue
      
      // Type validation
      if (fieldSchema.type === 'number' && typeof value !== 'number') {
        return false
      }
      if (fieldSchema.type === 'string' && typeof value !== 'string') {
        return false
      }
      if (fieldSchema.type === 'boolean' && typeof value !== 'boolean') {
        return false
      }
      
      // Range validation for numbers
      if (fieldSchema.type === 'number' && typeof value === 'number') {
        if (fieldSchema.min !== undefined && value < fieldSchema.min) {
          return false
        }
        if (fieldSchema.max !== undefined && value > fieldSchema.max) {
          return false
        }
      }
      
      // Length validation for strings
      if (fieldSchema.type === 'string' && typeof value === 'string') {
        if (fieldSchema.minLength !== undefined && value.length < fieldSchema.minLength) {
          return false
        }
        if (fieldSchema.maxLength !== undefined && value.length > fieldSchema.maxLength) {
          return false
        }
      }
    }
    
    return true
  } catch (error) {
    console.error('Settings validation error:', error)
    return false
  }
}

export default useFeatureStore