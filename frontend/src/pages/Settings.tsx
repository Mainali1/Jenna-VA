import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  UserIcon,
  SpeakerWaveIcon,
  BellIcon,
  ShieldCheckIcon,
  KeyIcon,
  PaintBrushIcon,
  GlobeAltIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { cn } from '@utils/cn'
import type { UserPreferences, Theme } from '@/types'

interface SettingsProps {
  className?: string
  isElectron?: boolean
}

interface SettingsSectionProps {
  title: string
  description?: string
  icon: React.ComponentType<{ className?: string }>
  children: React.ReactNode
}

interface ToggleProps {
  enabled: boolean
  onChange: (enabled: boolean) => void
  label?: string
  description?: string
}

const Toggle: React.FC<ToggleProps> = ({ enabled, onChange, label, description }) => {
  return (
    <div className="flex items-center justify-between">
      <div>
        {label && (
          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
            {label}
          </h4>
        )}
        {description && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {description}
          </p>
        )}
      </div>
      <button
        type="button"
        className={cn(
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent',
          'transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          enabled ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'
        )}
        role="switch"
        aria-checked={enabled}
        onClick={() => onChange(!enabled)}
      >
        <span className="sr-only">Toggle</span>
        <span
          className={cn(
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0',
            'transition duration-200 ease-in-out',
            enabled ? 'translate-x-5' : 'translate-x-0'
          )}
        />
      </button>
    </div>
  )
}

const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  description,
  icon: Icon,
  children,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
          <Icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
      </div>
      <div className="space-y-6">
        {children}
      </div>
    </motion.div>
  )
}

const Settings: React.FC<SettingsProps> = ({ className, isElectron }) => {
  const { user, config, updateUserPreferences, updateTheme } = useAppStore()
  const [preferences, setPreferences] = useState<UserPreferences>(user?.preferences || {
    voice: {
      enabled: true,
      voice: 'en-US-Standard-J',
      speed: 1.0,
      pitch: 1.0,
      autoListen: false,
    },
    notifications: {
      enabled: true,
      sounds: true,
      updates: true,
      tips: true,
    },
    privacy: {
      saveHistory: true,
      analytics: true,
      shareUsageData: false,
    },
    shortcuts: {
      enabled: true,
      activationKey: 'Alt+Space',
      custom: {},
    },
    appearance: {
      theme: 'system',
      fontSize: 'medium',
      animations: true,
    },
    language: 'en-US',
    autoUpdate: true,
    startOnBoot: true,
  })
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState<boolean | null>(null)

  // Update preferences when user changes
  useEffect(() => {
    if (user?.preferences) {
      setPreferences(user.preferences)
    }
  }, [user?.preferences])

  // Handle preference changes
  const handlePreferenceChange = <T extends keyof UserPreferences>(
    section: T,
    key: keyof UserPreferences[T],
    value: any
  ) => {
    setPreferences(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }))
  }

  // Handle theme change
  const handleThemeChange = (theme: Theme) => {
    setPreferences(prev => ({
      ...prev,
      appearance: {
        ...prev.appearance,
        theme,
      },
    }))
    updateTheme(theme)
  }

  // Save preferences
  const handleSave = async () => {
    setIsSaving(true)
    setSaveSuccess(null)

    try {
      await updateUserPreferences(preferences)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(null), 3000)
    } catch (error) {
      console.error('Failed to save preferences:', error)
      setSaveSuccess(false)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className={cn('p-6 space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Customize your Jenna Voice Assistant experience
          </p>
        </div>

        {/* Save Button */}
        <div className="flex items-center space-x-4">
          {saveSuccess !== null && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className={cn(
                'flex items-center space-x-2 px-3 py-2 rounded-lg',
                saveSuccess
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                  : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
              )}
            >
              {saveSuccess ? (
                <CheckIcon className="w-5 h-5" />
              ) : (
                <XMarkIcon className="w-5 h-5" />
              )}
              <span className="text-sm font-medium">
                {saveSuccess ? 'Settings saved' : 'Failed to save'}
              </span>
            </motion.div>
          )}

          <button
            onClick={handleSave}
            disabled={isSaving}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors duration-200',
              'bg-blue-500 text-white hover:bg-blue-600',
              'disabled:bg-blue-300 disabled:cursor-not-allowed'
            )}
          >
            {isSaving ? (
              <span className="flex items-center space-x-2">
                <ArrowPathIcon className="w-4 h-4 animate-spin" />
                <span>Saving...</span>
              </span>
            ) : (
              'Save Changes'
            )}
          </button>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Section */}
        <SettingsSection
          title="Profile"
          description="Manage your account information"
          icon={UserIcon}
        >
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Display Name
              </label>
              <input
                type="text"
                id="name"
                value={user?.name || ''}
                onChange={(e) => {}}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={user?.email || ''}
                onChange={(e) => {}}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <button className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                Change Password
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Voice Settings */}
        <SettingsSection
          title="Voice"
          description="Configure voice recognition and speech settings"
          icon={SpeakerWaveIcon}
        >
          <div className="space-y-4">
            <Toggle
              enabled={preferences.voice?.enabled || false}
              onChange={(enabled) => handlePreferenceChange('voice', 'enabled', enabled)}
              label="Enable Voice Recognition"
              description="Allow Jenna to listen and respond to voice commands"
            />

            <div>
              <label htmlFor="voice" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Assistant Voice
              </label>
              <select
                id="voice"
                value={preferences.voice?.voice || 'en-US-Standard-J'}
                onChange={(e) => handlePreferenceChange('voice', 'voice', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="en-US-Standard-J">Jenna (Female)</option>
                <option value="en-US-Standard-B">Brian (Male)</option>
                <option value="en-US-Standard-E">Emma (Female)</option>
                <option value="en-US-Standard-D">David (Male)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Voice Speed: {preferences.voice?.speed || 1.0}x
              </label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={preferences.voice?.speed || 1.0}
                onChange={(e) => handlePreferenceChange('voice', 'speed', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Voice Pitch: {preferences.voice?.pitch || 1.0}
              </label>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.1"
                value={preferences.voice?.pitch || 1.0}
                onChange={(e) => handlePreferenceChange('voice', 'pitch', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <Toggle
              enabled={preferences.voice?.autoListen || false}
              onChange={(enabled) => handlePreferenceChange('voice', 'autoListen', enabled)}
              label="Auto-Listen Mode"
              description="Automatically start listening when idle"
            />
          </div>
        </SettingsSection>

        {/* Notifications */}
        <SettingsSection
          title="Notifications"
          description="Manage alerts and notification preferences"
          icon={BellIcon}
        >
          <div className="space-y-4">
            <Toggle
              enabled={preferences.notifications?.enabled || false}
              onChange={(enabled) => handlePreferenceChange('notifications', 'enabled', enabled)}
              label="Enable Notifications"
              description="Show system notifications for important events"
            />

            <Toggle
              enabled={preferences.notifications?.sounds || false}
              onChange={(enabled) => handlePreferenceChange('notifications', 'sounds', enabled)}
              label="Notification Sounds"
              description="Play sounds for notifications"
            />

            <Toggle
              enabled={preferences.notifications?.updates || false}
              onChange={(enabled) => handlePreferenceChange('notifications', 'updates', enabled)}
              label="Update Notifications"
              description="Get notified about new updates"
            />

            <Toggle
              enabled={preferences.notifications?.tips || false}
              onChange={(enabled) => handlePreferenceChange('notifications', 'tips', enabled)}
              label="Tips & Suggestions"
              description="Receive helpful tips about using Jenna"
            />
          </div>
        </SettingsSection>

        {/* Privacy */}
        <SettingsSection
          title="Privacy"
          description="Control your data and privacy settings"
          icon={ShieldCheckIcon}
        >
          <div className="space-y-4">
            <Toggle
              enabled={preferences.privacy?.saveHistory || false}
              onChange={(enabled) => handlePreferenceChange('privacy', 'saveHistory', enabled)}
              label="Save Conversation History"
              description="Store your conversations for future reference"
            />

            <Toggle
              enabled={preferences.privacy?.analytics || false}
              onChange={(enabled) => handlePreferenceChange('privacy', 'analytics', enabled)}
              label="Usage Analytics"
              description="Help improve Jenna by sharing anonymous usage data"
            />

            <Toggle
              enabled={preferences.privacy?.shareUsageData || false}
              onChange={(enabled) => handlePreferenceChange('privacy', 'shareUsageData', enabled)}
              label="Share Voice Data"
              description="Contribute voice samples to improve recognition (optional)"
            />

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <button className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium block">
                Export My Data
              </button>
              <button className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium block">
                Delete All My Data
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Keyboard Shortcuts */}
        <SettingsSection
          title="Keyboard Shortcuts"
          description="Customize keyboard shortcuts for quick access"
          icon={KeyIcon}
        >
          <div className="space-y-4">
            <Toggle
              enabled={preferences.shortcuts?.enabled || false}
              onChange={(enabled) => handlePreferenceChange('shortcuts', 'enabled', enabled)}
              label="Enable Keyboard Shortcuts"
              description="Use keyboard shortcuts to control Jenna"
            />

            <div>
              <label htmlFor="activationKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Activation Shortcut
              </label>
              <input
                type="text"
                id="activationKey"
                value={preferences.shortcuts?.activationKey || 'Alt+Space'}
                onChange={(e) => handlePreferenceChange('shortcuts', 'activationKey', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Press the keys you want to use as the shortcut
              </p>
            </div>

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Common Shortcuts
              </h4>
              <div className="space-y-2">
                {[
                  { label: 'Start Listening', shortcut: 'Ctrl+Shift+L' },
                  { label: 'New Conversation', shortcut: 'Ctrl+N' },
                  { label: 'Open Settings', shortcut: 'Ctrl+,' },
                  { label: 'Toggle Sidebar', shortcut: 'Ctrl+B' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {item.label}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono text-gray-800 dark:text-gray-200">
                      {item.shortcut}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* Appearance */}
        <SettingsSection
          title="Appearance"
          description="Customize the look and feel of the application"
          icon={PaintBrushIcon}
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Theme
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'light', label: 'Light' },
                  { value: 'dark', label: 'Dark' },
                  { value: 'system', label: 'System' },
                ].map((theme) => (
                  <button
                    key={theme.value}
                    type="button"
                    className={cn(
                      'flex items-center justify-center px-3 py-2 border rounded-lg',
                      preferences.appearance?.theme === theme.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                        : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    )}
                    onClick={() => handleThemeChange(theme.value as Theme)}
                  >
                    {theme.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Font Size
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'small', label: 'Small' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'large', label: 'Large' },
                ].map((size) => (
                  <button
                    key={size.value}
                    type="button"
                    className={cn(
                      'flex items-center justify-center px-3 py-2 border rounded-lg',
                      preferences.appearance?.fontSize === size.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                        : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    )}
                    onClick={() => handlePreferenceChange('appearance', 'fontSize', size.value)}
                  >
                    {size.label}
                  </button>
                ))}
              </div>
            </div>

            <Toggle
              enabled={preferences.appearance?.animations || false}
              onChange={(enabled) => handlePreferenceChange('appearance', 'animations', enabled)}
              label="Enable Animations"
              description="Show animations and transitions in the interface"
            />
          </div>
        </SettingsSection>

        {/* Language */}
        <SettingsSection
          title="Language"
          description="Set your preferred language"
          icon={GlobeAltIcon}
        >
          <div className="space-y-4">
            <div>
              <label htmlFor="language" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Interface Language
              </label>
              <select
                id="language"
                value={preferences.language || 'en-US'}
                onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
                <option value="ja-JP">Japanese</option>
                <option value="zh-CN">Chinese (Simplified)</option>
              </select>
            </div>
          </div>
        </SettingsSection>

        {/* System */}
        <SettingsSection
          title="System"
          description="Configure system-level settings"
          icon={ArrowPathIcon}
        >
          <div className="space-y-4">
            <Toggle
              enabled={preferences.autoUpdate || false}
              onChange={(enabled) => setPreferences({ ...preferences, autoUpdate: enabled })}
              label="Automatic Updates"
              description="Automatically download and install updates"
            />

            <Toggle
              enabled={preferences.startOnBoot || false}
              onChange={(enabled) => setPreferences({ ...preferences, startOnBoot: enabled })}
              label="Start on System Boot"
              description="Launch Jenna when your computer starts"
            />
            
            {isElectron && (
              <>
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Connection Type
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { value: 'grpc', label: 'gRPC (Recommended)' },
                      { value: 'websocket', label: 'WebSocket' },
                    ].map((type) => (
                      <button
                        key={type.value}
                        type="button"
                        className={cn(
                          'flex items-center justify-center px-3 py-2 border rounded-lg',
                          preferences.connection?.type === type.value
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                            : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                        )}
                        onClick={() => handlePreferenceChange('connection', 'type', type.value)}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    gRPC provides faster performance for desktop app. WebSocket is used as fallback.
                  </p>
                </div>
                
                <Toggle
                  enabled={preferences.desktopNotifications || false}
                  onChange={(enabled) => setPreferences({ ...preferences, desktopNotifications: enabled })}
                  label="Desktop Notifications"
                  description="Show system notifications for important events"
                />
              </>
            )}

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Current Version
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {config?.version || '1.0.0'}
                  </p>
                </div>
                <button className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200">
                  <ArrowPathIcon className="w-4 h-4" />
                  <span className="text-sm">Check for Updates</span>
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Backup & Restore
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Save or restore your settings and data
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="flex items-center space-x-1 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200">
                    <CloudArrowUpIcon className="w-4 h-4" />
                    <span className="text-sm">Backup</span>
                  </button>
                  <button className="flex items-center space-x-1 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200">
                    <ArrowPathIcon className="w-4 h-4" />
                    <span className="text-sm">Restore</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  )
}

export default Settings