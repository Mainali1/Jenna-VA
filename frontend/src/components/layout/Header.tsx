import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  WifiIcon,
  SignalIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { useConversationStore } from '@store/conversationStore'
import { cn } from '@utils/cn'

interface HeaderProps {
  className?: string
  onMenuToggle?: () => void
  isElectron?: boolean
}

const Header: React.FC<HeaderProps> = ({ className, onMenuToggle, isElectron }) => {
  const { 
    currentUser, 
    theme, 
    setTheme, 
    connectionStatus, 
    isListening,
    config 
  } = useAppStore()
  const { searchConversations, clearSearch, searchQuery } = useConversationStore()
  
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [searchValue, setSearchValue] = useState(searchQuery)
  const [notifications] = useState([
    {
      id: '1',
      title: 'Feature Update',
      message: 'New voice recognition improvements available',
      time: '2 minutes ago',
      type: 'info',
      read: false,
    },
    {
      id: '2',
      title: 'System Status',
      message: 'All services are running normally',
      time: '1 hour ago',
      type: 'success',
      read: true,
    },
  ])
  
  const userMenuRef = useRef<HTMLDivElement>(null)
  const notificationRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Handle search
  const handleSearch = (value: string) => {
    setSearchValue(value)
    if (value.trim()) {
      searchConversations(value)
    } else {
      clearSearch()
    }
  }

  // Handle theme change
  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme)
    setShowUserMenu(false)
  }

  // Handle logout
  const handleLogout = () => {
    // Dispatch logout event
    const event = new CustomEvent('jenna:logout')
    window.dispatchEvent(event)
    setShowUserMenu(false)
  }

  // Get connection status icon and color
  const getConnectionStatus = () => {
    switch (connectionStatus) {
      case 'connected':
        return { icon: WifiIcon, color: 'text-green-500', label: 'Connected' }
      case 'connecting':
        return { icon: SignalIcon, color: 'text-yellow-500', label: 'Connecting...' }
      case 'disconnected':
        return { icon: ExclamationTriangleIcon, color: 'text-red-500', label: 'Disconnected' }
      default:
        return { icon: WifiIcon, color: 'text-gray-400', label: 'Unknown' }
    }
  }

  const connectionInfo = getConnectionStatus()
  const unreadNotifications = notifications.filter(n => !n.read).length

  return (
    <header className={cn(
      'flex items-center justify-between px-6 py-4',
      'bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700',
      'shadow-sm backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95',
      'relative z-20',
      className
    )}>
      {/* Left Section */}
      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            ref={searchRef}
            type="text"
            placeholder="Search conversations..."
            value={searchValue}
            onChange={(e) => handleSearch(e.target.value)}
            className={cn(
              'block w-80 pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600',
              'rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
              'placeholder-gray-500 dark:placeholder-gray-400',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
              'transition-all duration-200'
            )}
          />
          {searchValue && (
            <button
              onClick={() => handleSearch('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Center Section - Status Indicators */}
      <div className="flex items-center space-x-4">
        {/* Listening Status */}
        <AnimatePresence>
          {isListening && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center space-x-2 px-3 py-1 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-full"
            >
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Listening...</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <connectionInfo.icon className={cn('w-5 h-5', connectionInfo.color)} />
            <span className={cn('text-sm', connectionInfo.color)}>
              {connectionInfo.label}
              {isElectron && (
                <span className="text-xs ml-1 text-gray-500 dark:text-gray-400">
                  [Electron]
                </span>
              )}
            </span>
          </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <div className="relative" ref={notificationRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className={cn(
              'relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
              'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white',
              'transition-colors duration-200'
            )}
          >
            <BellIcon className="w-6 h-6" />
            {unreadNotifications > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadNotifications}
              </span>
            )}
          </button>

          <AnimatePresence>
            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
              >
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Notifications
                  </h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length > 0 ? (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={cn(
                          'p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0',
                          'hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors',
                          !notification.read && 'bg-blue-50 dark:bg-blue-900/10'
                        )}
                      >
                        <div className="flex items-start space-x-3">
                          <div className={cn(
                            'w-2 h-2 rounded-full mt-2',
                            notification.type === 'info' && 'bg-blue-500',
                            notification.type === 'success' && 'bg-green-500',
                            notification.type === 'warning' && 'bg-yellow-500',
                            notification.type === 'error' && 'bg-red-500'
                          )} />
                          <div className="flex-1">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                              {notification.title}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                              {notification.time}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                      <BellIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No notifications</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* User Menu */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className={cn(
              'flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
              'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white',
              'transition-colors duration-200'
            )}
          >
            {currentUser?.avatar ? (
              <img
                src={currentUser.avatar}
                alt={currentUser.name}
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <UserCircleIcon className="w-8 h-8" />
            )}
            <span className="text-sm font-medium hidden md:block">
              {currentUser?.name || 'Guest'}
            </span>
            <ChevronDownIcon className="w-4 h-4" />
          </button>

          <AnimatePresence>
            {showUserMenu && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
              >
                {/* User Info */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-3">
                    {currentUser?.avatar ? (
                      <img
                        src={currentUser.avatar}
                        alt={currentUser.name}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    ) : (
                      <UserCircleIcon className="w-12 h-12 text-gray-400" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {currentUser?.name || 'Guest User'}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {currentUser?.email || 'Not signed in'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Theme Selection */}
                <div className="p-2">
                  <div className="px-2 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                    Theme
                  </div>
                  <div className="space-y-1">
                    {[
                      { value: 'light', label: 'Light', icon: SunIcon },
                      { value: 'dark', label: 'Dark', icon: MoonIcon },
                      { value: 'system', label: 'System', icon: ComputerDesktopIcon },
                    ].map((themeOption) => {
                      const Icon = themeOption.icon
                      return (
                        <button
                          key={themeOption.value}
                          onClick={() => handleThemeChange(themeOption.value as any)}
                          className={cn(
                            'w-full flex items-center space-x-2 px-3 py-2 rounded-md text-sm',
                            'hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors',
                            theme === themeOption.value
                              ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                              : 'text-gray-700 dark:text-gray-300'
                          )}
                        >
                          <Icon className="w-4 h-4" />
                          <span>{themeOption.label}</span>
                          {theme === themeOption.value && (
                            <div className="ml-auto w-2 h-2 bg-primary-500 rounded-full" />
                          )}
                        </button>
                      )
                    })}
                  </div>
                </div>

                <div className="border-t border-gray-200 dark:border-gray-700 p-2">
                  {/* Settings */}
                  <button
                    onClick={() => {
                      window.location.hash = '/settings'
                      setShowUserMenu(false)
                    }}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Cog6ToothIcon className="w-4 h-4" />
                    <span>Settings</span>
                  </button>

                  {/* Logout */}
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-md text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  >
                    <ArrowRightOnRectangleIcon className="w-4 h-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}

export default Header