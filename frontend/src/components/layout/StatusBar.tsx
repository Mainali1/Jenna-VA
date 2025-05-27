import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CpuChipIcon,
  CircleStackIcon,
  WifiIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { cn } from '@utils/cn'

interface StatusBarProps {
  className?: string
}

interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: {
    upload: number
    download: number
  }
}

const StatusBar: React.FC<StatusBarProps> = ({ className }) => {
  const { connectionStatus, config, isListening } = useAppStore()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isExpanded, setIsExpanded] = useState(false)
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: { upload: 0, download: 0 },
  })
  const [logs, setLogs] = useState([
    {
      id: '1',
      level: 'info',
      message: 'Voice engine initialized successfully',
      timestamp: new Date(Date.now() - 30000),
    },
    {
      id: '2',
      level: 'success',
      message: 'Connected to AI service',
      timestamp: new Date(Date.now() - 15000),
    },
    {
      id: '3',
      level: 'warning',
      message: 'High CPU usage detected',
      timestamp: new Date(Date.now() - 5000),
    },
  ])

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Simulate system metrics updates
  useEffect(() => {
    const updateMetrics = () => {
      setSystemMetrics({
        cpu: Math.random() * 100,
        memory: 45 + Math.random() * 30,
        disk: 65 + Math.random() * 10,
        network: {
          upload: Math.random() * 1000,
          download: Math.random() * 5000,
        },
      })
    }

    updateMetrics()
    const interval = setInterval(updateMetrics, 5000)

    return () => clearInterval(interval)
  }, [])

  // Format bytes
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  // Format time
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-500'
      case 'connecting':
        return 'text-yellow-500'
      case 'disconnected':
        return 'text-red-500'
      default:
        return 'text-gray-400'
    }
  }

  // Get log level icon and color
  const getLogLevelInfo = (level: string) => {
    switch (level) {
      case 'error':
        return { icon: ExclamationTriangleIcon, color: 'text-red-500' }
      case 'warning':
        return { icon: ExclamationTriangleIcon, color: 'text-yellow-500' }
      case 'success':
        return { icon: CheckCircleIcon, color: 'text-green-500' }
      case 'info':
      default:
        return { icon: InformationCircleIcon, color: 'text-blue-500' }
    }
  }

  const recentLogs = logs.slice(-3).reverse()

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700',
      'shadow-sm backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95',
      className
    )}>
      {/* Main Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 text-sm">
        {/* Left Section - System Metrics */}
        <div className="flex items-center space-x-6">
          {/* CPU */}
          <div className="flex items-center space-x-2">
            <CpuChipIcon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">CPU:</span>
            <span className={cn(
              'font-medium',
              systemMetrics.cpu > 80 ? 'text-red-500' :
              systemMetrics.cpu > 60 ? 'text-yellow-500' : 'text-green-500'
            )}>
              {systemMetrics.cpu.toFixed(1)}%
            </span>
          </div>

          {/* Memory */}
          <div className="flex items-center space-x-2">
            <CircleStackIcon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">RAM:</span>
            <span className={cn(
              'font-medium',
              systemMetrics.memory > 80 ? 'text-red-500' :
              systemMetrics.memory > 60 ? 'text-yellow-500' : 'text-green-500'
            )}>
              {systemMetrics.memory.toFixed(1)}%
            </span>
          </div>

          {/* Network */}
          <div className="flex items-center space-x-2">
            <WifiIcon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">Network:</span>
            <span className="text-green-500 font-medium">
              ↓{formatBytes(systemMetrics.network.download)}/s
            </span>
            <span className="text-blue-500 font-medium">
              ↑{formatBytes(systemMetrics.network.upload)}/s
            </span>
          </div>
        </div>

        {/* Center Section - Status */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={cn(
              'w-2 h-2 rounded-full',
              connectionStatus === 'connected' ? 'bg-green-500' :
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
              'bg-red-500'
            )} />
            <span className={cn('capitalize', getStatusColor(connectionStatus))}>
              {connectionStatus}
            </span>
          </div>

          {/* Listening Status */}
          <AnimatePresence>
            {isListening && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex items-center space-x-2 px-2 py-1 bg-red-100 dark:bg-red-900/20 rounded-full"
              >
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-red-700 dark:text-red-400 text-xs font-medium">
                  Recording
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Recent Activity */}
          {recentLogs.length > 0 && (
            <div className="flex items-center space-x-2">
              {(() => {
                const latestLog = recentLogs[0]
                const logInfo = getLogLevelInfo(latestLog.level)
                const Icon = logInfo.icon
                return (
                  <>
                    <Icon className={cn('w-4 h-4', logInfo.color)} />
                    <span className="text-gray-600 dark:text-gray-400 max-w-xs truncate">
                      {latestLog.message}
                    </span>
                  </>
                )
              })()} 
            </div>
          )}
        </div>

        {/* Right Section - Time and Controls */}
        <div className="flex items-center space-x-4">
          {/* Current Time */}
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400 font-mono">
              {formatTime(currentTime)}
            </span>
          </div>

          {/* Version */}
          <span className="text-gray-500 dark:text-gray-500 text-xs">
            v{config?.version || '1.0.0'}
          </span>

          {/* Expand/Collapse Button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={cn(
              'p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800',
              'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
              'transition-colors duration-200'
            )}
          >
            {isExpanded ? (
              <ChevronDownIcon className="w-4 h-4" />
            ) : (
              <ChevronUpIcon className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded Section */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <div className="p-4 space-y-4">
              {/* Detailed Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* System Performance */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    System Performance
                  </h4>
                  <div className="space-y-2">
                    {[
                      { label: 'CPU Usage', value: systemMetrics.cpu, unit: '%', max: 100 },
                      { label: 'Memory Usage', value: systemMetrics.memory, unit: '%', max: 100 },
                      { label: 'Disk Usage', value: systemMetrics.disk, unit: '%', max: 100 },
                    ].map((metric) => (
                      <div key={metric.label} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600 dark:text-gray-400">
                            {metric.label}
                          </span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {metric.value.toFixed(1)}{metric.unit}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className={cn(
                              'h-2 rounded-full transition-all duration-300',
                              metric.value > 80 ? 'bg-red-500' :
                              metric.value > 60 ? 'bg-yellow-500' : 'bg-green-500'
                            )}
                            style={{ width: `${(metric.value / metric.max) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Network Activity */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Network Activity
                  </h4>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Download:</span>
                      <span className="text-green-500 font-medium">
                        {formatBytes(systemMetrics.network.download)}/s
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Upload:</span>
                      <span className="text-blue-500 font-medium">
                        {formatBytes(systemMetrics.network.upload)}/s
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Status:</span>
                      <span className={cn('font-medium capitalize', getStatusColor(connectionStatus))}>
                        {connectionStatus}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Recent Logs */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Recent Activity
                  </h4>
                  <div className="space-y-2 max-h-24 overflow-y-auto">
                    {recentLogs.map((log) => {
                      const logInfo = getLogLevelInfo(log.level)
                      const Icon = logInfo.icon
                      return (
                        <div key={log.id} className="flex items-start space-x-2 text-xs">
                          <Icon className={cn('w-3 h-3 mt-0.5 flex-shrink-0', logInfo.color)} />
                          <div className="flex-1 min-w-0">
                            <p className="text-gray-900 dark:text-white truncate">
                              {log.message}
                            </p>
                            <p className="text-gray-500 dark:text-gray-500">
                              {formatTime(log.timestamp)}
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default StatusBar