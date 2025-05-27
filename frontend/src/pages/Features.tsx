import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  PlusIcon,
  CheckIcon,
  XMarkIcon,
  ChevronRightIcon,
  Cog6ToothIcon,
  ClockIcon,
  CalendarDaysIcon,
  SunIcon,
  BookOpenIcon,
  MusicalNoteIcon,
  DocumentTextIcon,
  CalculatorIcon,
  MapIcon,
  ShoppingCartIcon,
  BriefcaseIcon,
  HeartIcon,
} from '@heroicons/react/24/outline'
import { useFeatureStore } from '@store/featureStore'
import { cn } from '@utils/cn'
import type { Feature, FeatureCategory } from '@/types'

interface FeaturesProps {
  className?: string
}

interface FeatureCardProps {
  feature: Feature
  onToggle: (id: string, enabled: boolean) => void
  onConfigure: (id: string) => void
}

interface CategoryFilterProps {
  categories: FeatureCategory[]
  selectedCategory: string | null
  onSelectCategory: (category: string | null) => void
}

const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  selectedCategory,
  onSelectCategory,
}) => {
  return (
    <div className="flex items-center space-x-2 overflow-x-auto pb-2 hide-scrollbar">
      <button
        onClick={() => onSelectCategory(null)}
        className={cn(
          'px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap',
          'transition-colors duration-200',
          selectedCategory === null
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
        )}
      >
        All
      </button>

      {categories.map((category) => (
        <button
          key={category.id}
          onClick={() => onSelectCategory(category.id)}
          className={cn(
            'px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap',
            'transition-colors duration-200',
            selectedCategory === category.id
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          )}
        >
          {category.name}
        </button>
      ))}
    </div>
  )
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature, onToggle, onConfigure }) => {
  const [isHovered, setIsHovered] = useState(false)

  // Get icon component based on feature type
  const getIconComponent = () => {
    switch (feature.type) {
      case 'pomodoro':
        return ClockIcon
      case 'calendar':
        return CalendarDaysIcon
      case 'weather':
        return SunIcon
      case 'flashcards':
        return BookOpenIcon
      case 'music':
        return MusicalNoteIcon
      case 'notes':
        return DocumentTextIcon
      case 'calculator':
        return CalculatorIcon
      case 'maps':
        return MapIcon
      case 'shopping':
        return ShoppingCartIcon
      case 'tasks':
        return BriefcaseIcon
      case 'health':
        return HeartIcon
      default:
        return Cog6ToothIcon
    }
  }

  const Icon = getIconComponent()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
        'border border-gray-200 dark:border-gray-700',
        'hover:shadow-md transition-all duration-200',
        feature.enabled ? 'border-l-4 border-l-green-500' : ''
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className={cn(
            'p-3 rounded-lg',
            feature.enabled ? 'bg-green-100 dark:bg-green-900/20' : 'bg-gray-100 dark:bg-gray-700'
          )}>
            <Icon className={cn(
              'w-6 h-6',
              feature.enabled ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'
            )} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {feature.name}
              </h3>
              {feature.enabled && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                  Active
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {feature.description}
            </p>
            <div className="flex items-center space-x-4 mt-3">
              <button
                onClick={() => onToggle(feature.id, !feature.enabled)}
                className={cn(
                  'flex items-center space-x-1 text-sm font-medium',
                  'transition-colors duration-200',
                  feature.enabled
                    ? 'text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300'
                    : 'text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300'
                )}
              >
                {feature.enabled ? (
                  <>
                    <XMarkIcon className="w-4 h-4" />
                    <span>Disable</span>
                  </>
                ) : (
                  <>
                    <CheckIcon className="w-4 h-4" />
                    <span>Enable</span>
                  </>
                )}
              </button>
              <button
                onClick={() => onConfigure(feature.id)}
                className="flex items-center space-x-1 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200"
              >
                <Cog6ToothIcon className="w-4 h-4" />
                <span>Configure</span>
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={() => onConfigure(feature.id)}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors duration-200"
        >
          <ChevronRightIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Feature Stats (conditionally shown) */}
      {feature.enabled && feature.stats && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(feature.stats).map(([key, value]) => (
              <div key={key} className="text-sm">
                <span className="text-gray-500 dark:text-gray-400 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}:
                </span>
                <span className="ml-1 font-medium text-gray-900 dark:text-white">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

const Features: React.FC<FeaturesProps> = ({ className }) => {
  const { features, categories, isLoading, toggleFeature, updateFeatureSettings } = useFeatureStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [filteredFeatures, setFilteredFeatures] = useState<Feature[]>([])

  // Filter features based on search query and selected category
  useEffect(() => {
    let filtered = [...features]

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (feature) =>
          feature.name.toLowerCase().includes(query) ||
          feature.description.toLowerCase().includes(query)
      )
    }

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter((feature) => feature.categoryId === selectedCategory)
    }

    setFilteredFeatures(filtered)
  }, [features, searchQuery, selectedCategory])

  // Handle feature toggle
  const handleToggleFeature = (id: string, enabled: boolean) => {
    toggleFeature(id, enabled)
  }

  // Handle feature configuration
  const handleConfigureFeature = (id: string) => {
    // This would typically open a modal or navigate to a configuration page
    console.log(`Configure feature: ${id}`)
  }

  return (
    <div className={cn('p-6 space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Features
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Customize and manage available features
          </p>
        </div>

        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200">
          <PlusIcon className="w-5 h-5" />
          <span>Add Feature</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0 md:space-x-4">
        <div className="relative w-full md:w-96">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search features..."
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        <div className="flex items-center space-x-4">
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />

          <button className="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200">
            <AdjustmentsHorizontalIcon className="w-5 h-5" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Features Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-12 h-12 border-4 border-gray-200 dark:border-gray-700 border-t-blue-500 rounded-full animate-spin" />
            <p className="text-gray-600 dark:text-gray-400">Loading features...</p>
          </div>
        </div>
      ) : filteredFeatures.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
            <MagnifyingGlassIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No features found
          </h3>
          <p className="text-gray-600 dark:text-gray-400 max-w-md">
            {searchQuery || selectedCategory
              ? "We couldn't find any features matching your search criteria. Try adjusting your filters."
              : "There are no features available yet. Click 'Add Feature' to create one."}
          </p>
          {(searchQuery || selectedCategory) && (
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory(null)
              }}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200"
            >
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredFeatures.map((feature) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              onToggle={handleToggleFeature}
              onConfigure={handleConfigureFeature}
            />
          ))}
        </div>
      )}

      {/* Feature Stats Summary */}
      {features.length > 0 && (
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Feature Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="space-y-1">
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Features</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {features.length}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-500 dark:text-gray-400">Active Features</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {features.filter(f => f.enabled).length}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-500 dark:text-gray-400">Most Used</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {features.length > 0
                  ? features.sort((a, b) => (b.stats?.usageCount || 0) - (a.stats?.usageCount || 0))[0]?.name
                  : 'N/A'}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-500 dark:text-gray-400">Categories</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {categories.length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Features