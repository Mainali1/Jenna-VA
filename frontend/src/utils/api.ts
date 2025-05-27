import { ApiResponse, AppConfig, UserProfile, Conversation, Message, FeatureDefinition, SystemInfo, ActionResult, AnalyticsData } from '@/types'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Request types
type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

interface RequestOptions {
  method?: RequestMethod
  headers?: Record<string, string>
  body?: any
  timeout?: number
  signal?: AbortSignal
}

interface ApiRequestOptions extends RequestOptions {
  skipAuth?: boolean
  retries?: number
  retryDelay?: number
}

// Error classes
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class NetworkError extends Error {
  constructor(message: string, public originalError?: Error) {
    super(message)
    this.name = 'NetworkError'
  }
}

export class TimeoutError extends Error {
  constructor(message: string = 'Request timeout') {
    super(message)
    this.name = 'TimeoutError'
  }
}

// Auth token management
class AuthManager {
  private token: string | null = null
  private refreshToken: string | null = null
  private tokenExpiry: number | null = null

  setTokens(accessToken: string, refreshToken?: string, expiresIn?: number) {
    this.token = accessToken
    this.refreshToken = refreshToken || null
    this.tokenExpiry = expiresIn ? Date.now() + (expiresIn * 1000) : null
    
    // Store in localStorage for persistence
    localStorage.setItem('jenna_access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('jenna_refresh_token', refreshToken)
    }
    if (expiresIn) {
      localStorage.setItem('jenna_token_expiry', this.tokenExpiry!.toString())
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('jenna_access_token')
      const expiry = localStorage.getItem('jenna_token_expiry')
      this.tokenExpiry = expiry ? parseInt(expiry) : null
    }

    // Check if token is expired
    if (this.tokenExpiry && Date.now() > this.tokenExpiry) {
      this.clearTokens()
      return null
    }

    return this.token
  }

  clearTokens() {
    this.token = null
    this.refreshToken = null
    this.tokenExpiry = null
    localStorage.removeItem('jenna_access_token')
    localStorage.removeItem('jenna_refresh_token')
    localStorage.removeItem('jenna_token_expiry')
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) {
      this.refreshToken = localStorage.getItem('jenna_refresh_token')
    }

    if (!this.refreshToken) {
      return false
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      })

      if (!response.ok) {
        throw new Error('Failed to refresh token')
      }

      const data = await response.json()
      this.setTokens(data.access_token, data.refresh_token, data.expires_in)
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearTokens()
      return false
    }
  }
}

const authManager = new AuthManager()

// Request interceptor
class RequestInterceptor {
  private requestQueue: Array<() => Promise<any>> = []
  private isRefreshing = false

  async makeRequest<T>(
    url: string,
    options: ApiRequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = API_TIMEOUT,
      skipAuth = false,
      retries = 3,
      retryDelay = 1000,
      signal,
    } = options

    // Prepare headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    }

    // Add auth token if not skipped
    if (!skipAuth) {
      const token = authManager.getToken()
      if (token) {
        requestHeaders['Authorization'] = `Bearer ${token}`
      }
    }

    // Prepare request options
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      signal,
    }

    if (body && method !== 'GET') {
      requestOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
    }

    // Create timeout controller
    const timeoutController = new AbortController()
    const timeoutId = setTimeout(() => timeoutController.abort(), timeout)

    // Combine signals
    const combinedSignal = signal
      ? this.combineAbortSignals([signal, timeoutController.signal])
      : timeoutController.signal

    requestOptions.signal = combinedSignal

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, requestOptions)
      clearTimeout(timeoutId)

      // Handle 401 Unauthorized
      if (response.status === 401 && !skipAuth) {
        const refreshed = await this.handleTokenRefresh()
        if (refreshed) {
          // Retry the request with new token
          return this.makeRequest(url, { ...options, retries: 0 })
        } else {
          // Redirect to login or handle auth failure
          window.dispatchEvent(new CustomEvent('jenna:auth-failed'))
          throw new ApiError('Authentication failed', 401, 'AUTH_FAILED')
        }
      }

      const responseData = await this.parseResponse(response)

      if (!response.ok) {
        throw new ApiError(
          responseData.message || `HTTP ${response.status}`,
          response.status,
          responseData.code,
          responseData.details
        )
      }

      return responseData
    } catch (error) {
      clearTimeout(timeoutId)

      if (error instanceof ApiError) {
        throw error
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        if (signal?.aborted) {
          throw new Error('Request was cancelled')
        } else {
          throw new TimeoutError()
        }
      }

      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Network connection failed', error)
      }

      // Retry logic for network errors
      if (retries > 0 && this.shouldRetry(error)) {
        await this.delay(retryDelay)
        return this.makeRequest(url, {
          ...options,
          retries: retries - 1,
          retryDelay: retryDelay * 2, // Exponential backoff
        })
      }

      throw error
    }
  }

  private async handleTokenRefresh(): Promise<boolean> {
    if (this.isRefreshing) {
      // Wait for ongoing refresh
      return new Promise((resolve) => {
        this.requestQueue.push(() => Promise.resolve(resolve(true)))
      })
    }

    this.isRefreshing = true
    const refreshed = await authManager.refreshAccessToken()
    this.isRefreshing = false

    // Process queued requests
    this.requestQueue.forEach(request => request())
    this.requestQueue = []

    return refreshed
  }

  private async parseResponse(response: Response): Promise<any> {
    const contentType = response.headers.get('content-type')
    
    if (contentType?.includes('application/json')) {
      return response.json()
    }
    
    if (contentType?.includes('text/')) {
      return { data: await response.text() }
    }
    
    return { data: await response.blob() }
  }

  private shouldRetry(error: any): boolean {
    // Retry on network errors, timeouts, and certain HTTP status codes
    return (
      error instanceof NetworkError ||
      error instanceof TimeoutError ||
      (error instanceof ApiError && [408, 429, 500, 502, 503, 504].includes(error.status || 0))
    )
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private combineAbortSignals(signals: AbortSignal[]): AbortSignal {
    const controller = new AbortController()
    
    signals.forEach(signal => {
      if (signal.aborted) {
        controller.abort()
      } else {
        signal.addEventListener('abort', () => controller.abort())
      }
    })
    
    return controller.signal
  }
}

const requestInterceptor = new RequestInterceptor()

// API client class
export class ApiClient {
  // Auth endpoints
  static async login(email: string, password: string): Promise<ApiResponse<{ user: UserProfile; tokens: any }>> {
    return requestInterceptor.makeRequest('/auth/login', {
      method: 'POST',
      body: { email, password },
      skipAuth: true,
    })
  }

  static async logout(): Promise<ApiResponse<void>> {
    const result = await requestInterceptor.makeRequest('/auth/logout', {
      method: 'POST',
    })
    authManager.clearTokens()
    return result
  }

  static async register(userData: Partial<UserProfile>): Promise<ApiResponse<{ user: UserProfile; tokens: any }>> {
    return requestInterceptor.makeRequest('/auth/register', {
      method: 'POST',
      body: userData,
      skipAuth: true,
    })
  }

  // User endpoints
  static async getCurrentUser(): Promise<ApiResponse<UserProfile>> {
    return requestInterceptor.makeRequest('/user/profile')
  }

  static async updateUser(userData: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    return requestInterceptor.makeRequest('/user/profile', {
      method: 'PUT',
      body: userData,
    })
  }

  static async updateUserPreferences(preferences: UserProfile['preferences']): Promise<ApiResponse<UserProfile>> {
    return requestInterceptor.makeRequest('/user/preferences', {
      method: 'PUT',
      body: preferences,
    })
  }

  // Configuration endpoints
  static async getConfig(): Promise<ApiResponse<AppConfig>> {
    return requestInterceptor.makeRequest('/config')
  }

  static async updateConfig(config: Partial<AppConfig>): Promise<ApiResponse<AppConfig>> {
    return requestInterceptor.makeRequest('/config', {
      method: 'PUT',
      body: config,
    })
  }

  // Voice endpoints
  static async sendVoiceCommand(audioBlob: Blob): Promise<ApiResponse<{ transcript: string; response: any }>> {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'voice_command.wav')
    
    return requestInterceptor.makeRequest('/voice/command', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    })
  }

  static async synthesizeSpeech(text: string, voice?: string): Promise<ApiResponse<Blob>> {
    return requestInterceptor.makeRequest('/voice/synthesize', {
      method: 'POST',
      body: { text, voice },
    })
  }

  // Chat endpoints
  static async getConversations(): Promise<ApiResponse<Conversation[]>> {
    return requestInterceptor.makeRequest('/chat/conversations')
  }

  static async getConversation(id: string): Promise<ApiResponse<Conversation>> {
    return requestInterceptor.makeRequest(`/chat/conversations/${id}`)
  }

  static async createConversation(title?: string): Promise<ApiResponse<Conversation>> {
    return requestInterceptor.makeRequest('/chat/conversations', {
      method: 'POST',
      body: { title },
    })
  }

  static async sendMessage(conversationId: string, content: string, type: 'text' | 'voice' = 'text'): Promise<ApiResponse<Message>> {
    return requestInterceptor.makeRequest(`/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: { content, type },
    })
  }

  static async deleteConversation(id: string): Promise<ApiResponse<void>> {
    return requestInterceptor.makeRequest(`/chat/conversations/${id}`, {
      method: 'DELETE',
    })
  }

  // Features endpoints
  static async getFeatures(): Promise<ApiResponse<FeatureDefinition[]>> {
    return requestInterceptor.makeRequest('/features')
  }

  static async getFeature(id: string): Promise<ApiResponse<FeatureDefinition>> {
    return requestInterceptor.makeRequest(`/features/${id}`)
  }

  static async toggleFeature(id: string, enabled: boolean): Promise<ApiResponse<FeatureDefinition>> {
    return requestInterceptor.makeRequest(`/features/${id}/toggle`, {
      method: 'POST',
      body: { enabled },
    })
  }

  static async updateFeatureSettings(id: string, settings: any): Promise<ApiResponse<FeatureDefinition>> {
    return requestInterceptor.makeRequest(`/features/${id}/settings`, {
      method: 'PUT',
      body: settings,
    })
  }

  // System endpoints
  static async getSystemInfo(): Promise<ApiResponse<SystemInfo>> {
    return requestInterceptor.makeRequest('/system/info')
  }

  static async getSystemHealth(): Promise<ApiResponse<{ status: string; services: any[] }>> {
    return requestInterceptor.makeRequest('/system/health')
  }

  static async executeAction(action: string, parameters?: any): Promise<ApiResponse<ActionResult>> {
    return requestInterceptor.makeRequest('/system/actions', {
      method: 'POST',
      body: { action, parameters },
    })
  }

  // Analytics endpoints
  static async getAnalytics(timeRange?: string): Promise<ApiResponse<AnalyticsData>> {
    const params = timeRange ? `?timeRange=${timeRange}` : ''
    return requestInterceptor.makeRequest(`/analytics${params}`)
  }

  static async trackEvent(event: string, data?: any): Promise<ApiResponse<void>> {
    return requestInterceptor.makeRequest('/analytics/events', {
      method: 'POST',
      body: { event, data, timestamp: Date.now() },
    })
  }

  // File operations
  static async uploadFile(file: File, path?: string): Promise<ApiResponse<{ path: string; url: string }>> {
    const formData = new FormData()
    formData.append('file', file)
    if (path) formData.append('path', path)
    
    return requestInterceptor.makeRequest('/files/upload', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    })
  }

  static async downloadFile(path: string): Promise<ApiResponse<Blob>> {
    return requestInterceptor.makeRequest(`/files/download?path=${encodeURIComponent(path)}`)
  }

  static async deleteFile(path: string): Promise<ApiResponse<void>> {
    return requestInterceptor.makeRequest('/files', {
      method: 'DELETE',
      body: { path },
    })
  }

  // Backup endpoints
  static async createBackup(): Promise<ApiResponse<{ backup_id: string; path: string }>> {
    return requestInterceptor.makeRequest('/backup/create', {
      method: 'POST',
    })
  }

  static async restoreBackup(backupId: string): Promise<ApiResponse<void>> {
    return requestInterceptor.makeRequest('/backup/restore', {
      method: 'POST',
      body: { backup_id: backupId },
    })
  }

  static async getBackups(): Promise<ApiResponse<Array<{ id: string; created_at: string; size: number }>>> {
    return requestInterceptor.makeRequest('/backup/list')
  }

  // Update endpoints
  static async checkForUpdates(): Promise<ApiResponse<{ available: boolean; version?: string; changelog?: string }>> {
    return requestInterceptor.makeRequest('/updates/check')
  }

  static async downloadUpdate(): Promise<ApiResponse<{ download_url: string }>> {
    return requestInterceptor.makeRequest('/updates/download', {
      method: 'POST',
    })
  }

  static async installUpdate(): Promise<ApiResponse<void>> {
    return requestInterceptor.makeRequest('/updates/install', {
      method: 'POST',
    })
  }
}

// Utility functions
export function setAuthTokens(accessToken: string, refreshToken?: string, expiresIn?: number) {
  authManager.setTokens(accessToken, refreshToken, expiresIn)
}

export function clearAuthTokens() {
  authManager.clearTokens()
}

export function getAuthToken(): string | null {
  return authManager.getToken()
}

// Request cancellation utility
export function createCancellableRequest<T>(
  requestFn: (signal: AbortSignal) => Promise<T>
): [Promise<T>, () => void] {
  const controller = new AbortController()
  const promise = requestFn(controller.signal)
  const cancel = () => controller.abort()
  
  return [promise, cancel]
}

// Batch request utility
export async function batchRequests<T>(
  requests: Array<() => Promise<T>>,
  batchSize: number = 5,
  delay: number = 100
): Promise<T[]> {
  const results: T[] = []
  
  for (let i = 0; i < requests.length; i += batchSize) {
    const batch = requests.slice(i, i + batchSize)
    const batchResults = await Promise.all(batch.map(request => request()))
    results.push(...batchResults)
    
    // Add delay between batches
    if (i + batchSize < requests.length && delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  return results
}

export default ApiClient