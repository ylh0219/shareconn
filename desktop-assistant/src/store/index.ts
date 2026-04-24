import { create } from 'zustand'
import { Task, Message } from '../types'

interface AssistantState {
  // 任务相关
  tasks: Task[]
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void
  updateTask: (id: string, task: Partial<Task>) => void
  deleteTask: (id: string) => void
  toggleTaskComplete: (id: string) => void
  
  // 消息相关
  messages: Message[]
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  clearMessages: () => void
  
  // 提醒相关
  setReminder: (taskId: string, time: Date) => void
  cancelReminder: (taskId: string) => void
  
  // 存储相关
  loadFromStorage: () => void
  saveToStorage: () => void
}

export const useAssistantStore = create<AssistantState>((set, get) => ({
  // 初始状态
  tasks: [],
  messages: [],
  
  // 任务相关方法
  addTask: (task) => {
    const newTask: Task = {
      ...task,
      id: Date.now().toString(),
      createdAt: new Date(),
      updatedAt: new Date()
    }
    set((state) => ({
      tasks: [...state.tasks, newTask]
    }))
    get().saveToStorage()
    get().setReminder(newTask.id, newTask.dueTime)
  },
  
  updateTask: (id, task) => {
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === id ? { ...t, ...task, updatedAt: new Date() } : t
      )
    }))
    get().saveToStorage()
  },
  
  deleteTask: (id) => {
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== id)
    }))
    get().saveToStorage()
    get().cancelReminder(id)
  },
  
  toggleTaskComplete: (id) => {
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === id ? { ...t, completed: !t.completed, updatedAt: new Date() } : t
      )
    }))
    get().saveToStorage()
  },
  
  // 消息相关方法
  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date()
    }
    set((state) => ({
      messages: [...state.messages, newMessage]
    }))
  },
  
  clearMessages: () => {
    set({ messages: [] })
  },
  
  // 提醒相关方法
  setReminder: (taskId, time) => {
    const task = get().tasks.find((t) => t.id === taskId)
    if (!task) return
    
    const now = new Date()
    const timeUntilReminder = time.getTime() - now.getTime()
    
    if (timeUntilReminder > 0) {
      const timeoutId = setTimeout(() => {
        if (window.electronAPI) {
          window.electronAPI.sendNotification(task)
        }
      }, timeUntilReminder)
      
      // 存储timeoutId以便后续取消
      localStorage.setItem(`reminder_${taskId}`, timeoutId.toString())
    }
  },
  
  cancelReminder: (taskId) => {
    const timeoutIdStr = localStorage.getItem(`reminder_${taskId}`)
    if (timeoutIdStr) {
      clearTimeout(parseInt(timeoutIdStr))
      localStorage.removeItem(`reminder_${taskId}`)
    }
  },
  
  // 存储相关方法
  loadFromStorage: () => {
    try {
      const tasks = localStorage.getItem('tasks')
      const messages = localStorage.getItem('messages')
      
      if (tasks) {
        const parsedTasks = JSON.parse(tasks)
        set({ tasks: parsedTasks })
        
        // 为每个任务设置提醒
        parsedTasks.forEach((task: Task) => {
          get().setReminder(task.id, new Date(task.dueTime))
        })
      }
      
      if (messages) {
        set({ messages: JSON.parse(messages) })
      }
    } catch (error) {
      console.error('Failed to load from storage:', error)
    }
  },
  
  saveToStorage: () => {
    try {
      const { tasks, messages } = get()
      localStorage.setItem('tasks', JSON.stringify(tasks))
      localStorage.setItem('messages', JSON.stringify(messages))
    } catch (error) {
      console.error('Failed to save to storage:', error)
    }
  }
}))