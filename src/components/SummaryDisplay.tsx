import { Share2, Copy, ExternalLink } from 'lucide-react'

export interface SummaryDisplayProps {
  title: string
  summary: string
  originalUrl: string
  onShare: () => void
  onCopy: () => void
}

const SummaryDisplay = ({ title, summary, originalUrl, onShare, onCopy }: SummaryDisplayProps) => {
  return (
    <div className="w-full max-w-3xl bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold text-gray-900 line-clamp-2">{title}</h2>
          <div className="flex gap-2">
            <button
              onClick={onCopy}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              title="复制摘要"
            >
              <Copy size={20} className="text-gray-600" />
            </button>
            <button
              onClick={onShare}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              title="分享摘要"
            >
              <Share2 size={20} className="text-gray-600" />
            </button>
          </div>
        </div>
        
        <div className="prose max-w-none mb-6">
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </div>
        
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <a
            href={originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-blue-500 hover:text-blue-600 text-sm font-medium"
          >
            查看原文
            <ExternalLink size={16} />
          </a>
          <span className="text-xs text-gray-500">
            {new Date().toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default SummaryDisplay