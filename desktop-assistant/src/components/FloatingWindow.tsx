import { useState, useRef, useEffect } from 'react'

interface FloatingWindowProps {
  title: string
  children: React.ReactNode
  onClose?: () => void
  onMinimize?: () => void
}

const FloatingWindow: React.FC<FloatingWindowProps> = ({ title, children, onClose, onMinimize }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const windowRef = useRef<HTMLDivElement>(null)

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX, y: e.clientY })
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging && window.electronAPI) {
      const deltaX = e.clientX - dragStart.x
      const deltaY = e.clientY - dragStart.y
      window.electronAPI.dragWindow(deltaX, deltaY)
      setDragStart({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, dragStart])

  return (
    <div 
      ref={windowRef}
      className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden"
      style={{ 
        width: '400px', 
        height: '500px',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)'
      }}
    >
      {/* 标题栏 */}
      <div 
        className="bg-indigo-600 text-white p-3 flex justify-between items-center cursor-move"
        onMouseDown={handleMouseDown}
      >
        <h2 className="font-medium text-sm">{title}</h2>
        <div className="flex space-x-2">
          {onMinimize && (
            <button 
              onClick={onMinimize}
              className="w-6 h-6 flex items-center justify-center rounded-full hover:bg-indigo-500 transition-colors"
            >
              <span className="text-xs">_</span>
            </button>
          )}
          {onClose && (
            <button 
              onClick={onClose}
              className="w-6 h-6 flex items-center justify-center rounded-full hover:bg-indigo-500 transition-colors"
            >
              <span className="text-xs">×</span>
            </button>
          )}
        </div>
      </div>
      
      {/* 内容区域 */}
      <div className="h-[calc(100%-48px)] overflow-y-auto">
        {children}
      </div>
    </div>
  )
}

export default FloatingWindow