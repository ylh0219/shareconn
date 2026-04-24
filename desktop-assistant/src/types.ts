export interface Task {
  id: string
  title: string
  description: string
  dueTime: Date
  priority: 'low' | 'medium' | 'high'
  completed: boolean
  recurring: boolean
  recurrencePattern: string
  createdAt: Date
  updatedAt: Date
}

export interface Reminder {
  taskId: string
  time: Date
  timeoutId: NodeJS.Timeout
}

export interface Message {
  id: string
  content: string
  sender: 'user' | 'assistant'
  timestamp: Date
}