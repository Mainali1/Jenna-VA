import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  ChartPieIcon,
  ClockIcon,
  CalendarDaysIcon,
  ChatBubbleLeftRightIcon,
  MicrophoneIcon,
  Cog6ToothIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
  AdjustmentsHorizontalIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline'
import { cn } from '@utils/cn'

interface AnalyticsProps {
  className?: string
}

interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
    borderWidth?: number
  }[]
}

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ComponentType<{ className?: string }>
  color: string
  trend?: 'up' | 'down' | 'neutral'
}

interface TimeRangeOption {
  value: string
  label: string
}

const timeRangeOptions: TimeRangeOption[] = [
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'This Quarter' },
  { value: 'year', label: 'This Year' },
  { value: 'custom', label: 'Custom Range' },
]

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
                vs previous period
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

const ChartContainer: React.FC<{
  title: string
  description?: string
  children: React.ReactNode
  className?: string
  icon: React.ComponentType<{ className?: string }>
}> = ({ title, description, children, className, icon: Icon }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm',
        'border border-gray-200 dark:border-gray-700',
        className
      )}
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
      {children}
    </motion.div>
  )
}

// Mock chart component (in a real app, you'd use a library like Chart.js or Recharts)
const Chart: React.FC<{
  type: 'bar' | 'line' | 'pie' | 'doughnut'
  data: ChartData
  height?: number
}> = ({ type, data, height = 300 }) => {
  // This is a placeholder for an actual chart component
  return (
    <div
      className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 flex items-center justify-center"
      style={{ height: `${height}px` }}
    >
      <div className="text-center">
        <p className="text-gray-500 dark:text-gray-400 mb-2">
          {type.charAt(0).toUpperCase() + type.slice(1)} Chart
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          {data.labels.length} data points across {data.datasets.length} datasets
        </p>
        <div className="mt-4 flex items-center justify-center space-x-2">
          {data.datasets.map((dataset, index) => (
            <div key={index} className="flex items-center space-x-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: dataset.backgroundColor || '#3B82F6' }}
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {dataset.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const Analytics: React.FC<AnalyticsProps> = ({ className }) => {
  const [timeRange, setTimeRange] = useState('week')
  const [isLoading, setIsLoading] = useState(false)

  // Mock data for charts
  const usageData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Conversations',
        data: [12, 19, 15, 22, 18, 10, 14],
        backgroundColor: '#3B82F6',
      },
      {
        label: 'Voice Commands',
        data: [8, 12, 10, 15, 12, 6, 9],
        backgroundColor: '#EC4899',
      },
    ],
  }

  const featureUsageData: ChartData = {
    labels: ['Pomodoro', 'Weather', 'Calendar', 'Notes', 'Flashcards', 'Music'],
    datasets: [
      {
        label: 'Usage Count',
        data: [45, 32, 28, 22, 18, 12],
        backgroundColor: [
          '#3B82F6', // blue
          '#10B981', // green
          '#F59E0B', // amber
          '#6366F1', // indigo
          '#EC4899', // pink
          '#8B5CF6', // purple
        ],
      },
    ],
  }

  const performanceData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Response Time (ms)',
        data: [320, 280, 310, 290, 350, 270, 300],
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
      },
    ],
  }

  const errorRateData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Error Rate (%)',
        data: [2.1, 1.8, 2.3, 1.5, 1.9, 1.2, 1.7],
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
      },
    ],
  }

  // Simulate loading data when time range changes
  useEffect(() => {
    setIsLoading(true)
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 800)

    return () => clearTimeout(timer)
  }, [timeRange])

  return (
    <div className={cn('p-6 space-y-6', className)}>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Insights and usage statistics
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Time Range Selector */}
          <div className="relative">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white pr-10"
            >
              {timeRangeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <CalendarDaysIcon className="h-5 w-5 text-gray-400" />
            </div>
          </div>

          {/* Export Button */}
          <button className="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200">
            <ArrowDownTrayIcon className="w-5 h-5" />
            <span>Export</span>
          </button>

          {/* Refresh Button */}
          <button
            className={cn(
              'p-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300',
              'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200'
            )}
            onClick={() => setTimeRange(timeRange)}
          >
            <ArrowPathIcon className={cn('w-5 h-5', isLoading && 'animate-spin')} />
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-12 h-12 border-4 border-gray-200 dark:border-gray-700 border-t-blue-500 rounded-full animate-spin" />
            <p className="text-gray-600 dark:text-gray-400">Loading analytics data...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Conversations"
              value="124"
              change={12}
              trend="up"
              icon={ChatBubbleLeftRightIcon}
              color="bg-blue-500"
            />
            <StatCard
              title="Voice Commands"
              value="87"
              change={-5}
              trend="down"
              icon={MicrophoneIcon}
              color="bg-purple-500"
            />
            <StatCard
              title="Active Features"
              value="8"
              change={25}
              trend="up"
              icon={Cog6ToothIcon}
              color="bg-green-500"
            />
            <StatCard
              title="Avg. Response Time"
              value="312ms"
              change={-8}
              trend="up"
              icon={ClockIcon}
              color="bg-amber-500"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Usage Over Time */}
            <ChartContainer
              title="Usage Over Time"
              description="Conversations and voice commands"
              icon={ChartBarIcon}
            >
              <Chart type="bar" data={usageData} />
            </ChartContainer>

            {/* Feature Usage */}
            <ChartContainer
              title="Feature Usage"
              description="Most used features"
              icon={ChartPieIcon}
            >
              <Chart type="pie" data={featureUsageData} />
            </ChartContainer>

            {/* Performance Metrics */}
            <ChartContainer
              title="Performance Metrics"
              description="Response time trends"
              icon={ClockIcon}
            >
              <Chart type="line" data={performanceData} />
            </ChartContainer>

            {/* Error Rates */}
            <ChartContainer
              title="Error Rates"
              description="Voice recognition and processing errors"
              icon={AdjustmentsHorizontalIcon}
            >
              <Chart type="line" data={errorRateData} />
            </ChartContainer>
          </div>

          {/* Detailed Stats */}
          <ChartContainer
            title="Detailed Statistics"
            description="Comprehensive usage breakdown"
            icon={ChartBarIcon}
            className="mt-6"
          >
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Metric
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Today
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      This Week
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      This Month
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Trend
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {[
                    {
                      metric: 'Total Conversations',
                      today: 18,
                      week: 124,
                      month: 487,
                      trend: 'up',
                    },
                    {
                      metric: 'Voice Commands',
                      today: 12,
                      week: 87,
                      month: 342,
                      trend: 'down',
                    },
                    {
                      metric: 'Average Session Duration',
                      today: '4m 12s',
                      week: '3m 58s',
                      month: '4m 05s',
                      trend: 'up',
                    },
                    {
                      metric: 'Error Rate',
                      today: '1.8%',
                      week: '2.1%',
                      month: '2.3%',
                      trend: 'down',
                    },
                    {
                      metric: 'Feature Activations',
                      today: 24,
                      week: 156,
                      month: 612,
                      trend: 'up',
                    },
                  ].map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {row.metric}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {row.today}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {row.week}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {row.month}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center">
                          {row.trend === 'up' ? (
                            <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                          ) : (
                            <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                          )}
                          <span className={cn(
                            row.trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                          )}>
                            {row.trend === 'up' ? 'Increasing' : 'Decreasing'}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartContainer>
        </>
      )}
    </div>
  )
}

export default Analytics