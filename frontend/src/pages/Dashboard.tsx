import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ChatBubbleLeftRightIcon,
  MicrophoneIcon,
  CpuChipIcon,
  ChartBarIcon,
  ClockIcon,
  UserIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  CalendarDaysIcon,
} from '@heroicons/react/24/outline'
import { useAppStore } from '@store/appStore'
import { useConversationStore } from '@store/conversationStore'
import { useFeatureStore } from '@store/featureStore'
import { cn } from '@utils/cn'

interface DashboardProps {
  className?: string
}

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ComponentType<{ className?: string }>
  color: string
  trend?: 'up' | 'down' | 'neutral'
}

interface ActivityItem {
  id: string
  type: 'conversation' | 'feature' | 'system'
  title: string
  description: string
  timestamp: Date
  icon: React.ComponentType<{ className?: string }>
  color: string
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  color,
  trend = 'neutral',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
        'border border-gray-200 dark:border-gray-700',
        'hover:shadow-md transition-shadow duration-200'
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {value}
          </p>
          {change !== undefined && (
            <div className="flex items-center mt-2">
              {trend === 'up' && (
                <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
              )}
              {trend === 'down' && (
                <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={cn(
                'text-sm font-medium',
                trend === 'up' ? 'text-green-600 dark:text-green-400' :
                trend === 'down' ? 'text-red-600 dark:text-red-400' :
                'text-gray-600 dark:text-gray-400'
              )}>
                {change > 0 ? '+' : ''}{change}%
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-500 ml-1">
                vs last week
              </span>
            </div>
          )}
        </div>
        <div className={cn(
          'p-3 rounded-lg',
          color
        )}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  )
}

const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const { user, config, connectionStatus } = useAppStore()
  const { conversations, stats: conversationStats } = useConversationStore()
  const { features, stats: featureStats } = useFeatureStore()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([])

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 60000)

    return () => clearInterval(timer)
  }, [])

  // Generate recent activity
  useEffect(() => {
    const activities: ActivityItem[] = [
      {
        id: '1',
        type: 'conversation',
        title: 'New conversation started',
        description: 'Asked about weather forecast',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        icon: ChatBubbleLeftRightIcon,
        color: 'text-blue-500',
      },
      {
        id: '2',
        type: 'feature',
        title: 'Pomodoro timer completed',
        description: '25-minute focus session finished',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        icon: ClockIcon,
        color: 'text-green-500',
      },
      {
        id: '3',
        type: 'system',
        title: 'Voice recognition improved',
        description: 'AI model updated successfully',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        icon: SparklesIcon,
        color: 'text-purple-500',
      },
      {
        id: '4',
        type: 'conversation',
        title: 'Voice command executed',
        description: 'Opened calendar application',
        timestamp: new Date(Date.now() - 45 * 60 * 1000),
        icon: MicrophoneIcon,
        color: 'text-red-500',
      },
      {
        id: '5',
        type: 'feature',
        title: 'Flashcard session completed',
        description: 'Reviewed 20 cards with 85% accuracy',
        timestamp: new Date(Date.now() - 60 * 60 * 1000),
        icon: EyeIcon,
        color: 'text-indigo-500',
      },
    ]

    setRecentActivity(activities)
  }, [])

  // Calculate stats
  const totalConversations = conversations.length
  const activeFeatures = features.filter(f => f.enabled).length
  const todayConversations = conversations.filter(
    c => new Date(c.createdAt).toDateString() === new Date().toDateString()
  ).length

  // Format time
  const formatTime = (date: Date): string => {
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Format relative time
  const formatRelativeTime = (date: Date): string => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  return (
    <div className={cn('p-6 space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.name || 'User'}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {formatTime(currentTime)}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={cn(
            'flex items-center space-x-2 px-3 py-2 rounded-lg',
            connectionStatus === 'connected' ? 'bg-green-100 dark:bg-green-900/20' :
            connectionStatus === 'connecting' ? 'bg-yellow-100 dark:bg-yellow-900/20' :
            'bg-red-100 dark:bg-red-900/20'
          )}>
            <div className={cn(
              'w-2 h-2 rounded-full',
              connectionStatus === 'connected' ? 'bg-green-500' :
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
              'bg-red-500'
            )} />
            <span className={cn(
              'text-sm font-medium capitalize',
              connectionStatus === 'connected' ? 'text-green-700 dark:text-green-400' :
              connectionStatus === 'connecting' ? 'text-yellow-700 dark:text-yellow-400' :
              'text-red-700 dark:text-red-400'
            )}>
              {connectionStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Conversations"
          value={totalConversations}
          change={12}
          trend="up"
          icon={ChatBubbleLeftRightIcon}
          color="bg-blue-500"
        />
        <StatCard
          title="Today's Chats"
          value={todayConversations}
          change={-5}
          trend="down"
          icon={CalendarDaysIcon}
          color="bg-green-500"
        />
        <StatCard
          title="Active Features"
          value={activeFeatures}
          change={8}
          trend="up"
          icon={Cog6ToothIcon}
          color="bg-purple-500"
        />
        <StatCard
          title="System Health"
          value="98%"
          change={2}
          trend="up"
          icon={CpuChipIcon}
          color="bg-orange-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className={cn(
              'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
              'border border-gray-200 dark:border-gray-700'
            )}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Recent Activity
              </h2>
              <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                View all
              </button>
            </div>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => {
                const Icon = activity.icon
                return (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="flex items-start space-x-4 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200"
                  >
                    <div className={cn(
                      'p-2 rounded-lg',
                      activity.type === 'conversation' ? 'bg-blue-100 dark:bg-blue-900/20' :
                      activity.type === 'feature' ? 'bg-green-100 dark:bg-green-900/20' :
                      'bg-purple-100 dark:bg-purple-900/20'
                    )}>
                      <Icon className={cn('w-5 h-5', activity.color)} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {activity.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {formatRelativeTime(activity.timestamp)}
                      </p>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </motion.div>
        </div>

        {/* Quick Actions & Stats */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className={cn(
              'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
              'border border-gray-200 dark:border-gray-700'
            )}
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h3>
            <div className="space-y-3">
              {[
                {
                  label: 'Start New Chat',
                  icon: ChatBubbleLeftRightIcon,
                  color: 'bg-blue-500 hover:bg-blue-600',
                  href: '/chat',
                },
                {
                  label: 'Voice Command',
                  icon: MicrophoneIcon,
                  color: 'bg-red-500 hover:bg-red-600',
                  action: 'voice',
                },
                {
                  label: 'View Analytics',
                  icon: ChartBarIcon,
                  color: 'bg-green-500 hover:bg-green-600',
                  href: '/analytics',
                },
                {
                  label: 'Settings',
                  icon: Cog6ToothIcon,
                  color: 'bg-purple-500 hover:bg-purple-600',
                  href: '/settings',
                },
              ].map((action, index) => {
                const Icon = action.icon
                return (
                  <motion.button
                    key={action.label}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className={cn(
                      'w-full flex items-center space-x-3 p-3 rounded-lg text-white',
                      'transition-colors duration-200',
                      action.color
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{action.label}</span>
                  </motion.button>
                )
              })}
            </div>
          </motion.div>

          {/* Usage Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className={cn(
              'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
              'border border-gray-200 dark:border-gray-700'
            )}
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Usage Statistics
            </h3>
            <div className="space-y-4">
              {[
                {
                  label: 'Messages Today',
                  value: conversationStats.totalMessages || 0,
                  max: 100,
                  color: 'bg-blue-500',
                },
                {
                  label: 'Voice Commands',
                  value: 23,
                  max: 50,
                  color: 'bg-red-500',
                },
                {
                  label: 'Features Used',
                  value: activeFeatures,
                  max: features.length,
                  color: 'bg-green-500',
                },
              ].map((stat) => (
                <div key={stat.label} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      {stat.label}
                    </span>
                    <span className="text-gray-900 dark:text-white font-medium">
                      {stat.value}/{stat.max}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={cn(
                        'h-2 rounded-full transition-all duration-300',
                        stat.color
                      )}
                      style={{ width: `${(stat.value / stat.max) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard