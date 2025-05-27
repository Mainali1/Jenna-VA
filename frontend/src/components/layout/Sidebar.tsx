import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  CogIcon,
  PuzzlePieceIcon,
  ChartBarIcon,
  QuestionMarkCircleIcon,
  Bars3Icon,
  XMarkIcon,
  MicrophoneIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { useConversationStore } from '@store/conversationStore'
import { useFeatureStore } from '@store/featureStore'
import { cn } from '@utils/cn'

interface SidebarProps {
  isCollapsed?: boolean
  onToggle?: () => void
  className?: string
}

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    description: 'Overview and quick actions',
  },
  {
    name: 'Chat',
    href: '/chat',
    icon: ChatBubbleLeftRightIcon,
    description: 'Conversation with Jenna',
  },
  {
    name: 'Features',
    href: '/features',
    icon: PuzzlePieceIcon,
    description: 'Manage available features',
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
    description: 'Usage statistics and insights',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: CogIcon,
    description: 'Configure preferences',
  },
  {
    name: 'Help',
    href: '/help',
    icon: QuestionMarkCircleIcon,
    description: 'Documentation and support',
  },
]

const Sidebar: React.FC<SidebarProps> = ({ 
  isCollapsed = false, 
  onToggle,
  className 
}) => {
  const location = useLocation()
  const { currentUser, isListening, config } = useAppStore()
  const { getConversationStats } = useConversationStore()
  const { getFeatureStats } = useFeatureStore()
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)

  const conversationStats = getConversationStats()
  const featureStats = getFeatureStats()

  const sidebarVariants = {
    expanded: {
      width: '280px',
      transition: {
        duration: 0.3,
        ease: 'easeInOut',
      },
    },
    collapsed: {
      width: '80px',
      transition: {
        duration: 0.3,
        ease: 'easeInOut',
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: {
        duration: 0.2,
        ease: 'easeOut',
      },
    },
  }

  const handleToggleListening = () => {
    const event = new CustomEvent('jenna:toggle-listening')
    window.dispatchEvent(event)
  }

  return (
    <motion.aside
      variants={sidebarVariants}
      animate={isCollapsed ? 'collapsed' : 'expanded'}
      className={cn(
        'flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700',
        'shadow-lg backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95',
        'relative z-30',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center space-x-3"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">J</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Jenna
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Voice Assistant
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <button
          onClick={onToggle}
          className={cn(
            'p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
            'transition-colors duration-200',
            'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          )}
        >
          {isCollapsed ? (
            <Bars3Icon className="w-5 h-5" />
          ) : (
            <XMarkIcon className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* User Profile */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="relative">
            {currentUser?.avatar ? (
              <img
                src={currentUser.avatar}
                alt={currentUser.name}
                className="w-10 h-10 rounded-full object-cover"
              />
            ) : (
              <UserCircleIcon className="w-10 h-10 text-gray-400" />
            )}
            <div className={cn(
              'absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white dark:border-gray-900',
              config?.status === 'online' ? 'bg-green-500' : 'bg-gray-400'
            )} />
          </div>
          
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {currentUser?.name || 'Guest User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {currentUser?.email || 'Not signed in'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Voice Control */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={handleToggleListening}
          className={cn(
            'w-full flex items-center justify-center space-x-2 p-3 rounded-lg',
            'transition-all duration-200 transform hover:scale-105',
            isListening
              ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/25'
              : 'bg-primary-500 hover:bg-primary-600 text-white shadow-lg shadow-primary-500/25'
          )}
        >
          <MicrophoneIcon className={cn(
            'w-5 h-5',
            isListening && 'animate-pulse'
          )} />
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-sm font-medium"
              >
                {isListening ? 'Stop Listening' : 'Start Listening'}
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon
          
          return (
            <motion.div
              key={item.name}
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              onHoverStart={() => setHoveredItem(item.name)}
              onHoverEnd={() => setHoveredItem(null)}
            >
              <Link
                to={item.href}
                className={cn(
                  'group flex items-center space-x-3 p-3 rounded-lg transition-all duration-200',
                  'hover:bg-gray-100 dark:hover:bg-gray-800',
                  isActive
                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 border-r-2 border-primary-500'
                    : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                )}
              >
                <Icon className={cn(
                  'w-5 h-5 flex-shrink-0',
                  isActive ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'
                )} />
                
                <AnimatePresence mode="wait">
                  {!isCollapsed && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      className="flex-1 min-w-0"
                    >
                      <span className="text-sm font-medium truncate">
                        {item.name}
                      </span>
                      {hoveredItem === item.name && (
                        <motion.p
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="text-xs text-gray-500 dark:text-gray-400 mt-1"
                        >
                          {item.description}
                        </motion.p>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
                
                {/* Badge for certain items */}
                {!isCollapsed && (
                  <AnimatePresence>
                    {item.name === 'Chat' && conversationStats.today > 0 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        className="bg-primary-500 text-white text-xs px-2 py-1 rounded-full"
                      >
                        {conversationStats.today}
                      </motion.span>
                    )}
                    {item.name === 'Features' && featureStats.enabled > 0 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        className="bg-green-500 text-white text-xs px-2 py-1 rounded-full"
                      >
                        {featureStats.enabled}
                      </motion.span>
                    )}
                  </AnimatePresence>
                )}
              </Link>
              
              {/* Tooltip for collapsed state */}
              {isCollapsed && hoveredItem === item.name && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="absolute left-20 top-0 z-50 bg-gray-900 dark:bg-gray-700 text-white text-sm px-3 py-2 rounded-lg shadow-lg whitespace-nowrap"
                >
                  {item.name}
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45" />
                </motion.div>
              )}
            </motion.div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="space-y-2"
            >
              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-50 dark:bg-gray-800 p-2 rounded">
                  <p className="text-gray-500 dark:text-gray-400">Conversations</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {conversationStats.total}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-2 rounded">
                  <p className="text-gray-500 dark:text-gray-400">Features</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {featureStats.enabled}/{featureStats.total}
                  </p>
                </div>
              </div>
              
              {/* Version */}
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Version {config?.version || '1.0.0'}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  )
}

export default Sidebar