import { useEffect, useCallback, useRef } from 'react'
import { useAppStore } from '@store/appStore'

type ShortcutHandler = () => void
type ShortcutMap = Record<string, ShortcutHandler>

interface UseKeyboardShortcutsOptions {
  enabled?: boolean
  preventDefault?: boolean
  stopPropagation?: boolean
  target?: HTMLElement | Document | Window
}

/**
 * Custom hook for handling keyboard shortcuts
 * 
 * @param shortcuts - Object mapping keyboard shortcuts to handler functions
 * @param options - Configuration options
 * 
 * @example
 * ```tsx
 * useKeyboardShortcuts({
 *   'ctrl+s': () => save(),
 *   'ctrl+shift+p': () => openCommandPalette(),
 *   'escape': () => closeModal(),
 *   'ctrl+/': () => toggleHelp()
 * })
 * ```
 */
export function useKeyboardShortcuts(
  shortcuts: ShortcutMap,
  options: UseKeyboardShortcutsOptions = {}
) {
  const {
    enabled = true,
    preventDefault = true,
    stopPropagation = false,
    target = document,
  } = options

  const shortcutsRef = useRef(shortcuts)
  const enabledRef = useRef(enabled)

  // Update refs when props change
  useEffect(() => {
    shortcutsRef.current = shortcuts
  }, [shortcuts])

  useEffect(() => {
    enabledRef.current = enabled
  }, [enabled])

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabledRef.current) return

    // Don't trigger shortcuts when typing in input fields
    const activeElement = document.activeElement
    const isInputField = activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.tagName === 'SELECT' ||
      activeElement.hasAttribute('contenteditable')
    )

    // Allow certain shortcuts even in input fields (like Escape)
    const allowedInInputs = ['escape', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']
    const shortcutKey = createShortcutKey(event)
    
    if (isInputField && !allowedInInputs.includes(shortcutKey.toLowerCase())) {
      return
    }

    const handler = shortcutsRef.current[shortcutKey]
    
    if (handler) {
      if (preventDefault) {
        event.preventDefault()
      }
      if (stopPropagation) {
        event.stopPropagation()
      }
      
      try {
        handler()
      } catch (error) {
        console.error('Error executing keyboard shortcut:', error)
      }
    }
  }, [preventDefault, stopPropagation])

  useEffect(() => {
    if (!enabled) return

    const targetElement = target as EventTarget
    targetElement.addEventListener('keydown', handleKeyDown)

    return () => {
      targetElement.removeEventListener('keydown', handleKeyDown)
    }
  }, [target, handleKeyDown, enabled])
}

/**
 * Creates a standardized shortcut key string from a keyboard event
 */
function createShortcutKey(event: KeyboardEvent): string {
  const parts: string[] = []
  
  // Add modifiers in a consistent order
  if (event.ctrlKey || event.metaKey) parts.push('ctrl')
  if (event.altKey) parts.push('alt')
  if (event.shiftKey) parts.push('shift')
  
  // Add the main key
  const key = event.key.toLowerCase()
  
  // Handle special keys
  const specialKeys: Record<string, string> = {
    ' ': 'space',
    'arrowup': 'up',
    'arrowdown': 'down',
    'arrowleft': 'left',
    'arrowright': 'right',
    'enter': 'enter',
    'escape': 'escape',
    'tab': 'tab',
    'backspace': 'backspace',
    'delete': 'delete',
    'home': 'home',
    'end': 'end',
    'pageup': 'pageup',
    'pagedown': 'pagedown',
    'insert': 'insert',
  }
  
  const normalizedKey = specialKeys[key] || key
  parts.push(normalizedKey)
  
  return parts.join('+')
}

/**
 * Hook for global application shortcuts
 * Uses the user's configured shortcuts from the app store
 */
export function useGlobalShortcuts() {
  const { currentUser } = useAppStore()
  const shortcuts = currentUser?.preferences.shortcuts

  const globalShortcuts: ShortcutMap = {
    // Default shortcuts that can be overridden by user preferences
    'ctrl+shift+j': () => {
      // Toggle listening
      const event = new CustomEvent('jenna:toggle-listening')
      window.dispatchEvent(event)
    },
    'ctrl+shift+s': () => {
      // Open settings
      window.location.hash = '/settings'
    },
    'ctrl+shift+h': () => {
      // Open help
      window.location.hash = '/help'
    },
    'ctrl+shift+d': () => {
      // Go to dashboard
      window.location.hash = '/dashboard'
    },
    'ctrl+shift+c': () => {
      // Open chat
      window.location.hash = '/chat'
    },
    'ctrl+shift+f': () => {
      // Open features
      window.location.hash = '/features'
    },
    'ctrl+shift+a': () => {
      // Open analytics
      window.location.hash = '/analytics'
    },
    'escape': () => {
      // Close modals/overlays
      const event = new CustomEvent('jenna:close-overlays')
      window.dispatchEvent(event)
    },
    'f1': () => {
      // Open help
      window.location.hash = '/help'
    },
    'ctrl+,': () => {
      // Open settings (alternative)
      window.location.hash = '/settings'
    },
    'ctrl+/': () => {
      // Show keyboard shortcuts help
      const event = new CustomEvent('jenna:show-shortcuts')
      window.dispatchEvent(event)
    },
  }

  // Override with user-configured shortcuts if available
  if (shortcuts) {
    if (shortcuts.toggleListening) {
      delete globalShortcuts['ctrl+shift+j']
      globalShortcuts[shortcuts.toggleListening] = () => {
        const event = new CustomEvent('jenna:toggle-listening')
        window.dispatchEvent(event)
      }
    }
    if (shortcuts.openSettings) {
      delete globalShortcuts['ctrl+shift+s']
      globalShortcuts[shortcuts.openSettings] = () => {
        window.location.hash = '/settings'
      }
    }
    if (shortcuts.openHelp) {
      delete globalShortcuts['ctrl+shift+h']
      globalShortcuts[shortcuts.openHelp] = () => {
        window.location.hash = '/help'
      }
    }
    if (shortcuts.goToDashboard) {
      delete globalShortcuts['ctrl+shift+d']
      globalShortcuts[shortcuts.goToDashboard] = () => {
        window.location.hash = '/dashboard'
      }
    }
    if (shortcuts.openChat) {
      delete globalShortcuts['ctrl+shift+c']
      globalShortcuts[shortcuts.openChat] = () => {
        window.location.hash = '/chat'
      }
    }
  }

  useKeyboardShortcuts(globalShortcuts, {
    enabled: true,
    preventDefault: true,
    stopPropagation: false,
  })
}

/**
 * Hook for modal/dialog shortcuts
 */
export function useModalShortcuts({
  onClose,
  onConfirm,
  onCancel,
  enabled = true,
}: {
  onClose?: () => void
  onConfirm?: () => void
  onCancel?: () => void
  enabled?: boolean
}) {
  const modalShortcuts: ShortcutMap = {}

  if (onClose) {
    modalShortcuts['escape'] = onClose
  }
  
  if (onConfirm) {
    modalShortcuts['enter'] = onConfirm
    modalShortcuts['ctrl+enter'] = onConfirm
  }
  
  if (onCancel) {
    modalShortcuts['ctrl+escape'] = onCancel
  }

  useKeyboardShortcuts(modalShortcuts, {
    enabled,
    preventDefault: true,
    stopPropagation: true,
  })
}

/**
 * Hook for form shortcuts
 */
export function useFormShortcuts({
  onSave,
  onCancel,
  onReset,
  enabled = true,
}: {
  onSave?: () => void
  onCancel?: () => void
  onReset?: () => void
  enabled?: boolean
}) {
  const formShortcuts: ShortcutMap = {}

  if (onSave) {
    formShortcuts['ctrl+s'] = onSave
    formShortcuts['ctrl+enter'] = onSave
  }
  
  if (onCancel) {
    formShortcuts['escape'] = onCancel
  }
  
  if (onReset) {
    formShortcuts['ctrl+r'] = onReset
  }

  useKeyboardShortcuts(formShortcuts, {
    enabled,
    preventDefault: true,
    stopPropagation: false,
  })
}

/**
 * Hook for navigation shortcuts
 */
export function useNavigationShortcuts({
  onNext,
  onPrevious,
  onFirst,
  onLast,
  enabled = true,
}: {
  onNext?: () => void
  onPrevious?: () => void
  onFirst?: () => void
  onLast?: () => void
  enabled?: boolean
}) {
  const navigationShortcuts: ShortcutMap = {}

  if (onNext) {
    navigationShortcuts['arrowright'] = onNext
    navigationShortcuts['pagedown'] = onNext
    navigationShortcuts['ctrl+arrowright'] = onNext
  }
  
  if (onPrevious) {
    navigationShortcuts['arrowleft'] = onPrevious
    navigationShortcuts['pageup'] = onPrevious
    navigationShortcuts['ctrl+arrowleft'] = onPrevious
  }
  
  if (onFirst) {
    navigationShortcuts['home'] = onFirst
    navigationShortcuts['ctrl+home'] = onFirst
  }
  
  if (onLast) {
    navigationShortcuts['end'] = onLast
    navigationShortcuts['ctrl+end'] = onLast
  }

  useKeyboardShortcuts(navigationShortcuts, {
    enabled,
    preventDefault: true,
    stopPropagation: false,
  })
}

/**
 * Utility function to format shortcut keys for display
 */
export function formatShortcut(shortcut: string): string {
  return shortcut
    .split('+')
    .map(key => {
      const keyMap: Record<string, string> = {
        'ctrl': '⌃',
        'cmd': '⌘',
        'alt': '⌥',
        'shift': '⇧',
        'enter': '↵',
        'escape': '⎋',
        'space': '␣',
        'tab': '⇥',
        'backspace': '⌫',
        'delete': '⌦',
        'up': '↑',
        'down': '↓',
        'left': '←',
        'right': '→',
        'pageup': '⇞',
        'pagedown': '⇟',
        'home': '⇱',
        'end': '⇲',
      }
      
      return keyMap[key.toLowerCase()] || key.toUpperCase()
    })
    .join('')
}

/**
 * Utility function to validate shortcut format
 */
export function isValidShortcut(shortcut: string): boolean {
  const parts = shortcut.toLowerCase().split('+')
  const validModifiers = ['ctrl', 'alt', 'shift', 'cmd', 'meta']
  const validKeys = /^[a-z0-9]$|^f[1-9]$|^f1[0-2]$|^(enter|escape|space|tab|backspace|delete|up|down|left|right|pageup|pagedown|home|end|insert)$/
  
  if (parts.length === 0) return false
  
  const key = parts[parts.length - 1]
  const modifiers = parts.slice(0, -1)
  
  // Check if key is valid
  if (!validKeys.test(key)) return false
  
  // Check if modifiers are valid
  for (const modifier of modifiers) {
    if (!validModifiers.includes(modifier)) return false
  }
  
  return true
}

export default useKeyboardShortcuts