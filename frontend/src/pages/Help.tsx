import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  QuestionMarkCircleIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  CommandLineIcon,
  CpuChipIcon,
  KeyIcon,
  MagnifyingGlassIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline'
import { cn } from '@utils/cn'

interface HelpProps {
  className?: string
}

interface FaqItem {
  question: string
  answer: string
  category: string
}

interface CommandExample {
  command: string
  description: string
  example: string
}

interface TutorialItem {
  title: string
  description: string
  videoUrl?: string
  steps: string[]
  icon: React.ComponentType<{ className?: string }>
}

const faqItems: FaqItem[] = [
  {
    question: 'How do I start a conversation with Jenna?',
    answer: 'You can start a conversation by clicking the microphone button in the sidebar or chat page, or by using the keyboard shortcut Alt+Space. You can also type your message in the chat input field.',
    category: 'basics',
  },
  {
    question: 'Can I customize Jenna\'s voice?',
    answer: 'Yes, you can customize Jenna\'s voice in the Settings page under the Voice section. You can choose from different voices, adjust the speech rate, and set the pitch.',
    category: 'customization',
  },
  {
    question: 'How do I enable or disable features?',
    answer: 'You can enable or disable features in the Features page. Simply toggle the switch next to each feature to turn it on or off. You can also configure each feature by clicking the settings icon.',
    category: 'features',
  },
  {
    question: 'Is my conversation data stored locally or in the cloud?',
    answer: 'By default, your conversation data is stored locally on your device. You can enable cloud sync in the Settings page under the Privacy section if you want to access your conversations across multiple devices.',
    category: 'privacy',
  },
  {
    question: 'How do I export my conversation history?',
    answer: 'You can export your conversation history in the Chat page by clicking the three dots menu in the top right corner and selecting "Export Conversation". You can choose to export as JSON, TXT, or PDF.',
    category: 'data',
  },
  {
    question: 'What should I do if Jenna doesn\'t understand my voice commands?',
    answer: 'If Jenna doesn\'t understand your voice commands, try speaking more clearly and in a quiet environment. You can also calibrate the microphone in the Settings page under the Voice section. Additionally, check if your microphone is properly connected and has the necessary permissions.',
    category: 'troubleshooting',
  },
  {
    question: 'How do I update Jenna to the latest version?',
    answer: 'Jenna checks for updates automatically when you start the application. You can also manually check for updates in the Settings page under the System section by clicking "Check for Updates".',
    category: 'system',
  },
  {
    question: 'Can I use Jenna offline?',
    answer: 'Yes, Jenna can work offline for basic functionality. However, some features like web search, weather updates, and cloud sync require an internet connection.',
    category: 'connectivity',
  },
]

const commandExamples: CommandExample[] = [
  {
    command: 'Set a timer',
    description: 'Creates a countdown timer',
    example: 'Set a timer for 10 minutes',
  },
  {
    command: 'Start Pomodoro',
    description: 'Starts a Pomodoro session',
    example: 'Start a Pomodoro session for 25 minutes',
  },
  {
    command: 'Check weather',
    description: 'Gets current weather information',
    example: 'What\'s the weather like in New York?',
  },
  {
    command: 'Create note',
    description: 'Creates a new note',
    example: 'Create a note about meeting agenda',
  },
  {
    command: 'Set reminder',
    description: 'Sets a reminder for a specific time',
    example: 'Remind me to call John at 3 PM',
  },
  {
    command: 'Play music',
    description: 'Plays music from your library',
    example: 'Play some jazz music',
  },
  {
    command: 'Summarize text',
    description: 'Summarizes long text',
    example: 'Summarize this article',
  },
  {
    command: 'Calculate',
    description: 'Performs mathematical calculations',
    example: 'What is 15% of 230?',
  },
]

const tutorials: TutorialItem[] = [
  {
    title: 'Getting Started with Jenna',
    description: 'Learn the basics of using Jenna Voice Assistant',
    steps: [
      'Launch the Jenna application',
      'Click on the microphone button in the sidebar',
      'Say "Hello Jenna" to start your first conversation',
      'Explore the dashboard to see available features',
    ],
    icon: MicrophoneIcon,
  },
  {
    title: 'Setting Up Voice Recognition',
    description: 'Optimize voice recognition for better accuracy',
    steps: [
      'Go to Settings > Voice',
      'Click on "Calibrate Microphone"',
      'Follow the on-screen instructions to speak test phrases',
      'Adjust microphone sensitivity if needed',
    ],
    icon: CpuChipIcon,
  },
  {
    title: 'Customizing Your Experience',
    description: 'Personalize Jenna to suit your preferences',
    steps: [
      'Go to Settings > Appearance',
      'Choose your preferred theme and color scheme',
      'Adjust text size and layout options',
      'Configure notification preferences',
    ],
    icon: KeyIcon,
  },
  {
    title: 'Using Advanced Commands',
    description: 'Learn how to use complex voice commands',
    steps: [
      'Start with basic commands like "What time is it?"',
      'Try chained commands like "Set a timer for 5 minutes and create a note"',
      'Experiment with context-aware commands',
      'Check the command reference for more examples',
    ],
    icon: CommandLineIcon,
  },
]

const Accordion: React.FC<{
  title: string
  children: React.ReactNode
  icon?: React.ComponentType<{ className?: string }>
  defaultOpen?: boolean
}> = ({ title, children, icon: Icon, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 text-left"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center space-x-3">
          {Icon && <Icon className="w-5 h-5 text-blue-500 dark:text-blue-400" />}
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        </div>
        {isOpen ? (
          <ChevronDownIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        ) : (
          <ChevronRightIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        )}
      </button>
      {isOpen && (
        <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          {children}
        </div>
      )}
    </div>
  )
}

const FaqSection: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'basics', name: 'Basics' },
    { id: 'customization', name: 'Customization' },
    { id: 'features', name: 'Features' },
    { id: 'privacy', name: 'Privacy & Data' },
    { id: 'troubleshooting', name: 'Troubleshooting' },
    { id: 'system', name: 'System' },
    { id: 'connectivity', name: 'Connectivity' },
  ]

  const filteredFaqs = faqItems.filter((item) => {
    const matchesSearch = searchQuery === '' || 
      item.question.toLowerCase().includes(searchQuery.toLowerCase()) || 
      item.answer.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Search FAQs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div>
          <select
            className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filteredFaqs.length === 0 ? (
        <div className="text-center py-8">
          <QuestionMarkCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900 dark:text-white">No FAQs found</h3>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            Try adjusting your search or filter to find what you're looking for.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFaqs.map((item, index) => (
            <Accordion 
              key={index} 
              title={item.question}
              icon={QuestionMarkCircleIcon}
              defaultOpen={index === 0}
            >
              <p className="text-gray-700 dark:text-gray-300">{item.answer}</p>
            </Accordion>
          ))}
        </div>
      )}
    </div>
  )
}

const CommandsSection: React.FC = () => {
  return (
    <div className="space-y-6">
      <p className="text-gray-700 dark:text-gray-300">
        Here are some common voice commands you can use with Jenna. Try these examples or variations to get started.
      </p>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Command
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Description
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Example
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {commandExamples.map((command, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700'}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {command.command}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  {command.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  <span className="italic">{command.example}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};