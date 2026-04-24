import { Clock } from 'lucide-react'

export interface HistoryItem {
  id: string
  url: string
  title: string
  summary: string
  timestamp: string
}

export interface HistoryListProps {
  history: HistoryItem[]
  onItemClick: (item: HistoryItem) => void
}

const HistoryList = ({ history, onItemClick }: HistoryListProps) => {
  if (history.length === 0) {
    return (
      <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <Clock size={48} className="mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">暂无历史记录</h3>
        <p className="text-gray-500">解析链接后，历史记录将显示在这里</p>
      </div>
    )
  }

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <h3 className="font-medium text-gray-900">历史记录</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {history.map((item) => (
          <div
            key={item.id}
            className="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => onItemClick(item)}
          >
            <div className="flex justify-between items-start">
              <h4 className="text-sm font-medium text-gray-900 line-clamp-1">
                {item.title}
              </h4>
              <span className="text-xs text-gray-500">
                {new Date(item.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-xs text-gray-500 line-clamp-1 mt-1">
              {item.url}
            </p>
            <p className="text-xs text-gray-600 line-clamp-2 mt-2">
              {item.summary}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HistoryList