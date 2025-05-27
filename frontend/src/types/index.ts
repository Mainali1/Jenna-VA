// Global type definitions for Jenna Voice Assistant

// ============================================================================
// Application Types
// ============================================================================

export type AppStatus = 
  | 'initializing'
  | 'ready'
  | 'listening'
  | 'processing'
  | 'speaking'
  | 'error'
  | 'offline'

export type ConnectionStatus = 
  | 'connected'
  | 'connecting'
  | 'disconnected'
  | 'reconnecting'
  | 'error'

export type Theme = 'dark' | 'light' | 'auto'

export interface AppConfig {
  version: string
  buildDate: string
  apiUrl: string
  wsUrl: string
  features: FeatureFlags
  limits: AppLimits
}

export interface AppLimits {
  maxConversationHistory: number
  maxFileSize: number
  maxConcurrentRequests: number
  requestTimeout: number
}

export interface FeatureFlags {
  voiceRecognition: boolean
  textToSpeech: boolean
  weatherService: boolean
  emailIntegration: boolean
  fileOperations: boolean
  pomodoroTimer: boolean
  flashcards: boolean
  analytics: boolean
  backupSystem: boolean
  autoUpdates: boolean
}

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: string
  name: string
  email?: string
  avatar?: string
  preferences: UserPreferences
  createdAt: string
  lastActiveAt: string
}

export interface UserPreferences {
  theme: Theme
  language: string
  voiceSettings: VoiceSettings
  notifications: NotificationSettings
  privacy: PrivacySettings
  shortcuts: KeyboardShortcuts
}

export interface VoiceSettings {
  wakePhrase: string
  voiceSpeed: number
  voicePitch: number
  voiceVolume: number
  selectedVoice: string
  noiseReduction: boolean
  autoListen: boolean
  confirmationSounds: boolean
}

export interface NotificationSettings {
  enabled: boolean
  soundEnabled: boolean
  showInSystemTray: boolean
  emailNotifications: boolean
  reminderNotifications: boolean
}

export interface PrivacySettings {
  saveConversations: boolean
  shareAnalytics: boolean
  allowCloudSync: boolean
  dataRetentionDays: number
}

export interface KeyboardShortcuts {
  toggleListening: string
  openSettings: string
  openHelp: string
  goToDashboard: string
  openChat: string
}

// ============================================================================
// Voice & AI Types
// ============================================================================

export interface VoiceCommand {
  id: string
  text: string
  confidence: number
  timestamp: string
  processed: boolean
  response?: string
}

export interface AIResponse {
  id: string
  text: string
  type: 'text' | 'action' | 'error'
  confidence: number
  timestamp: string
  metadata?: Record<string, any>
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
  tags: string[]
}

export interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: MessageMetadata
}

export interface MessageMetadata {
  confidence?: number
  processingTime?: number
  voiceData?: VoiceData
  actions?: ActionResult[]
}

export interface VoiceData {
  duration: number
  sampleRate: number
  channels: number
  format: string
}

// ============================================================================
// Feature Types
// ============================================================================

export interface Feature {
  id: string
  name: string
  description: string
  enabled: boolean
  category: FeatureCategory
  icon: string
  settings?: FeatureSettings
  dependencies?: string[]
  apiKeyRequired?: boolean
}

export type FeatureCategory = 
  | 'core'
  | 'productivity'
  | 'entertainment'
  | 'communication'
  | 'system'
  | 'ai'

export interface FeatureSettings {
  [key: string]: any
}

// Pomodoro Timer
export interface PomodoroSession {
  id: string
  type: 'work' | 'short-break' | 'long-break'
  duration: number
  startTime: string
  endTime?: string
  completed: boolean
  interrupted: boolean
}

export interface PomodoroStats {
  totalSessions: number
  completedSessions: number
  totalFocusTime: number
  averageSessionLength: number
  streakDays: number
}

// Flashcards
export interface Flashcard {
  id: string
  front: string
  back: string
  category: string
  difficulty: 'easy' | 'medium' | 'hard'
  lastReviewed?: string
  nextReview?: string
  reviewCount: number
  correctCount: number
  tags: string[]
}

export interface FlashcardDeck {
  id: string
  name: string
  description: string
  cards: Flashcard[]
  createdAt: string
  updatedAt: string
  settings: DeckSettings
}

export interface DeckSettings {
  spacedRepetition: boolean
  shuffleCards: boolean
  showHints: boolean
  autoAdvance: boolean
}

// Weather
export interface WeatherData {
  location: string
  temperature: number
  condition: string
  humidity: number
  windSpeed: number
  windDirection: string
  pressure: number
  visibility: number
  uvIndex: number
  forecast: WeatherForecast[]
  lastUpdated: string
}

export interface WeatherForecast {
  date: string
  high: number
  low: number
  condition: string
  precipitation: number
  humidity: number
}

// ============================================================================
// System Types
// ============================================================================

export interface SystemInfo {
  platform: string
  version: string
  architecture: string
  memory: MemoryInfo
  cpu: CpuInfo
  disk: DiskInfo
  network: NetworkInfo
}

export interface MemoryInfo {
  total: number
  used: number
  available: number
  percentage: number
}

export interface CpuInfo {
  model: string
  cores: number
  usage: number
  temperature?: number
}

export interface DiskInfo {
  total: number
  used: number
  available: number
  percentage: number
}

export interface NetworkInfo {
  connected: boolean
  type: 'wifi' | 'ethernet' | 'cellular' | 'unknown'
  speed?: number
  latency?: number
}

// ============================================================================
// Action Types
// ============================================================================

export interface Action {
  id: string
  type: ActionType
  name: string
  description: string
  parameters: ActionParameter[]
  category: string
  icon: string
  enabled: boolean
}

export type ActionType = 
  | 'system'
  | 'file'
  | 'application'
  | 'web'
  | 'communication'
  | 'media'
  | 'productivity'

export interface ActionParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'file' | 'directory'
  required: boolean
  description: string
  defaultValue?: any
  validation?: ParameterValidation
}

export interface ParameterValidation {
  min?: number
  max?: number
  pattern?: string
  allowedValues?: any[]
}

export interface ActionResult {
  id: string
  actionId: string
  success: boolean
  result?: any
  error?: string
  timestamp: string
  duration: number
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsData {
  usage: UsageStats
  performance: PerformanceStats
  features: FeatureUsageStats
  errors: ErrorStats
  timeRange: TimeRange
}

export interface UsageStats {
  totalCommands: number
  voiceCommands: number
  textCommands: number
  averageResponseTime: number
  sessionsToday: number
  totalSessionTime: number
  mostUsedFeatures: FeatureUsage[]
}

export interface PerformanceStats {
  averageResponseTime: number
  memoryUsage: number
  cpuUsage: number
  networkLatency: number
  errorRate: number
  uptime: number
}

export interface FeatureUsageStats {
  [featureId: string]: FeatureUsage
}

export interface FeatureUsage {
  featureId: string
  name: string
  usageCount: number
  lastUsed: string
  averageResponseTime: number
  successRate: number
}

export interface ErrorStats {
  totalErrors: number
  errorsByType: { [type: string]: number }
  recentErrors: ErrorLog[]
}

export interface ErrorLog {
  id: string
  type: string
  message: string
  stack?: string
  timestamp: string
  context?: Record<string, any>
}

export interface TimeRange {
  start: string
  end: string
  period: 'hour' | 'day' | 'week' | 'month' | 'year'
}

// ============================================================================
// WebSocket Types
// ============================================================================

export interface WebSocketMessage {
  type: WebSocketMessageType
  data?: any
  timestamp: string
  id?: string
}

export type WebSocketMessageType = 
  | 'ping'
  | 'pong'
  | 'status_update'
  | 'voice_command'
  | 'ai_response'
  | 'feature_toggle'
  | 'settings_update'
  | 'error'
  | 'notification'

export interface WebSocketConfig {
  url: string
  reconnectAttempts: number
  reconnectDelay: number
  heartbeatInterval: number
  timeout: number
}

// ============================================================================
// API Types
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: ApiError
  timestamp: string
  requestId: string
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
  hasPrevious: boolean
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

export interface InputProps extends BaseComponentProps {
  type?: string
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  error?: string
  disabled?: boolean
  required?: boolean
}

// ============================================================================
// Store Types
// ============================================================================

export interface AppStore {
  // State
  status: AppStatus
  connectionStatus: ConnectionStatus
  isListening: boolean
  currentUser: User | null
  theme: Theme
  config: AppConfig | null
  
  // Actions
  setStatus: (status: AppStatus) => void
  setConnectionStatus: (status: ConnectionStatus) => void
  setListening: (listening: boolean) => void
  setUser: (user: User | null) => void
  setTheme: (theme: Theme) => void
  setConfig: (config: AppConfig) => void
  initializeApp: () => Promise<void>
  cleanup: () => void
}

export interface ConversationStore {
  // State
  conversations: Conversation[]
  currentConversation: Conversation | null
  isLoading: boolean
  
  // Actions
  loadConversations: () => Promise<void>
  createConversation: (title?: string) => Conversation
  selectConversation: (id: string) => void
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => void
  deleteConversation: (id: string) => void
  clearConversations: () => void
}

export interface FeatureStore {
  // State
  features: Feature[]
  enabledFeatures: Set<string>
  isLoading: boolean
  
  // Actions
  loadFeatures: () => Promise<void>
  toggleFeature: (featureId: string) => Promise<void>
  updateFeatureSettings: (featureId: string, settings: FeatureSettings) => Promise<void>
  checkDependencies: (featureId: string) => boolean
}

// ============================================================================
// Utility Types
// ============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

export type ValueOf<T> = T[keyof T]

export type NonEmptyArray<T> = [T, ...T[]]

export type Prettify<T> = {
  [K in keyof T]: T[K]
} & {}