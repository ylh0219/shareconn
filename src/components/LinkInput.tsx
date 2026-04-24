import { useState } from 'react'
import { ArrowRight, Clipboard } from 'lucide-react'

export interface LinkInputProps {
  onSubmit: (url: string) => void
  isLoading: boolean
}

const LinkInput = ({ onSubmit, isLoading }: LinkInputProps) => {
  const [url, setUrl] = useState('')
  const [recentLinks, setRecentLinks] = useState<string[]>([])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      onSubmit(url.trim())
      setRecentLinks(prev => [url.trim(), ...prev.filter(link => link !== url.trim())].slice(0, 5))
      setUrl('')
    }
  }

  const handleRecentLinkClick = (link: string) => {
    setUrl(link)
  }

  return (
    <div className="w-full max-w-3xl">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="输入或粘贴分享链接..."
            className="w-full px-4 py-4 pr-16 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <ArrowRight size={20} />
            )}
          </button>
        </div>
        {recentLinks.length > 0 && (
          <div className="mt-2 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
            <div className="px-4 py-2 bg-gray-50 text-sm font-medium text-gray-600">
              最近链接
            </div>
            {recentLinks.map((link, index) => (
              <div
                key={index}
                className="px-4 py-2 text-sm hover:bg-gray-50 cursor-pointer flex items-center gap-2"
                onClick={() => handleRecentLinkClick(link)}
              >
                <Clipboard size={16} className="text-gray-400" />
                <span className="truncate">{link}</span>
              </div>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}

export default LinkInput