import { useState, useEffect } from 'react'
import { useAssistantStore } from '../store'

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('')
  const { messages, addMessage, loadFromStorage } = useAssistantStore()

  useEffect(() => {
    loadFromStorage()
  }, [loadFromStorage])

  const handleSend = () => {
    if (input.trim()) {
      // 添加用户消息
      addMessage({ content: input, sender: 'user' })
      
      // 生成助手回复
      setTimeout(() => {
        let response = ''
        
        // 简单的关键词匹配
        if (input.includes('你好') || input.includes('hi') || input.includes('hello')) {
          response = '你好！我是你的桌面小助手，有什么可以帮助你的吗？'
        } else if (input.includes('任务') || input.includes('计划')) {
          response = '好的，你可以告诉我具体的任务内容和时间，我会帮你设置提醒。'
        } else if (input.includes('谢谢')) {
          response = '不客气！随时为你服务。'
        } else {
          response = '我理解你的意思。你可以告诉我更多细节，或者直接创建一个任务。'
        }
        
        addMessage({ content: response, sender: 'assistant' })
      }, 1000)
      
      setInput('')
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* 消息列表 */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] p-3 rounded-lg ${message.sender === 'user' ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-800'}`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs text-gray-500 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>
      
      {/* 输入区域 */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入消息..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            onClick={handleSend}
            className="bg-indigo-600 hover:bg-indigo-700 text-white w-10 h-10 rounded-full flex items-center justify-center transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface