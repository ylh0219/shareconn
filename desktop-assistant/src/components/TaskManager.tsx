import { useState } from 'react'
import { useAssistantStore } from '../store'
import { Task } from '../types'

const TaskManager: React.FC = () => {
  const [showAddTask, setShowAddTask] = useState(false)
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    dueTime: new Date().toISOString().slice(0, 16),
    priority: 'medium' as 'low' | 'medium' | 'high',
    recurring: false,
    recurrencePattern: ''
  })
  const { tasks, addTask, deleteTask, toggleTaskComplete } = useAssistantStore()

  const handleAddTask = () => {
    if (newTask.title.trim()) {
      addTask({
        ...newTask,
        dueTime: new Date(newTask.dueTime),
        completed: false
      })
      setNewTask({
        title: '',
        description: '',
        dueTime: new Date().toISOString().slice(0, 16),
        priority: 'medium',
        recurring: false,
        recurrencePattern: ''
      })
      setShowAddTask(false)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-amber-100 text-amber-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-4 space-y-4">
      {/* 任务列表 */}
      <div className="space-y-2">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无任务，点击下方按钮添加
          </div>
        ) : (
          tasks.map((task) => (
            <div 
              key={task.id} 
              className="flex items-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggleTaskComplete(task.id)}
                className="mr-3"
              />
              <div className="flex-1">
                <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                  {task.title}
                </h3>
                <p className="text-xs text-gray-500">
                  {new Date(task.dueTime).toLocaleString()}
                </p>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                {task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}
              </span>
              <button
                onClick={() => deleteTask(task.id)}
                className="ml-2 text-gray-400 hover:text-red-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
      
      {/* 添加任务按钮 */}
      <button
        onClick={() => setShowAddTask(!showAddTask)}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg transition-colors flex items-center justify-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        添加任务
      </button>
      
      {/* 添加任务表单 */}
      {showAddTask && (
        <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg space-y-3">
          <h3 className="font-medium text-gray-900">添加任务</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              任务名称
            </label>
            <input
              type="text"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              placeholder="输入任务名称"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              描述
            </label>
            <textarea
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              placeholder="输入任务描述"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={2}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              提醒时间
            </label>
            <input
              type="datetime-local"
              value={newTask.dueTime}
              onChange={(e) => setNewTask({ ...newTask, dueTime: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              优先级
            </label>
            <select
              value={newTask.priority}
              onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as 'low' | 'medium' | 'high' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleAddTask}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg transition-colors"
            >
              保存
            </button>
            <button
              onClick={() => setShowAddTask(false)}
              className="px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded-lg transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default TaskManager