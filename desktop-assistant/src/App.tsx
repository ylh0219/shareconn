import { useState } from 'react'
import FloatingWindow from './components/FloatingWindow'
import ChatInterface from './components/ChatInterface'
import TaskManager from './components/TaskManager'

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'tasks'>('chat')

  const handleClose = () => {
    if (window.electronAPI) {
      window.electronAPI.closeWindow()
    }
  }

  const handleMinimize = () => {
    if (window.electronAPI) {
      window.electronAPI.minimizeWindow()
    }
  }

  return (
    <FloatingWindow 
      title="桌面小助手" 
      onClose={handleClose} 
      onMinimize={handleMinimize}
    >
      {/* 标签页 */}
      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'chat' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            聊天
          </button>
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'tasks' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            任务
          </button>
        </div>
      </div>
      
      {/* 内容区域 */}
      <div className="h-[calc(100%-64px)]">
        {activeTab === 'chat' ? (
          <ChatInterface />
        ) : (
          <TaskManager />
        )}
      </div>
    </FloatingWindow>
  )
}

export default App