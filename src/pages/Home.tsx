import { useState } from 'react'
import LinkInput from '../components/LinkInput'
import SummaryDisplay from '../components/SummaryDisplay'
import HistoryList from '../components/HistoryList'
import { HistoryItem } from '../components/HistoryList'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [summary, setSummary] = useState<{
    title: string
    summary: string
    originalUrl: string
  } | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])

  const handleParse = async (url: string) => {
    setIsLoading(true)
    try {
      // 调用后端API
      const response = await fetch('http://localhost:3001/api/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url })
      })
      
      const data = await response.json()
      
      if (data.success) {
        const { title, summary, originalUrl } = data.data
        setSummary({ title, summary, originalUrl })
        
        // 添加到历史记录
        const newHistoryItem: HistoryItem = {
          id: Date.now().toString(),
          url: originalUrl,
          title: title,
          summary: summary,
          timestamp: new Date().toISOString()
        }
        
        setHistory(prev => [newHistoryItem, ...prev].slice(0, 10))
      } else {
        alert('解析失败: ' + data.error)
      }
    } catch (error) {
      console.error('解析失败:', error)
      alert('解析失败，请稍后重试')
    } finally {
      setIsLoading(false)
    }
  }

  const handleShare = () => {
    if (summary) {
      if (navigator.share) {
        navigator.share({
          title: summary.title,
          text: summary.summary,
          url: summary.originalUrl
        })
      } else {
        // 降级方案
        const shareText = `${summary.title}\n\n${summary.summary}\n\n${summary.originalUrl}`
        navigator.clipboard.writeText(shareText)
        alert('分享内容已复制到剪贴板')
      }
    }
  }

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary.summary)
      alert('摘要已复制到剪贴板')
    }
  }

  const handleHistoryItemClick = (item: HistoryItem) => {
    setSummary({
      title: item.title,
      summary: item.summary,
      originalUrl: item.url
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            分享链接自动解析总结
          </h1>
          <p className="mt-2 text-gray-600">
            快速获取链接内容的核心信息，节省阅读时间
          </p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                输入链接
              </h2>
              <LinkInput onSubmit={handleParse} isLoading={isLoading} />
            </section>
            
            {summary && (
              <section>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  解析结果
                </h2>
                <SummaryDisplay
                  title={summary.title}
                  summary={summary.summary}
                  originalUrl={summary.originalUrl}
                  onShare={handleShare}
                  onCopy={handleCopy}
                />
              </section>
            )}
          </div>
          
          <div className="lg:col-span-1">
            <HistoryList
              history={history}
              onItemClick={handleHistoryItemClick}
            />
          </div>
        </div>
      </main>
      
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <p className="text-center text-gray-500 text-sm">
            © {new Date().getFullYear()} 分享链接自动解析总结服务
          </p>
        </div>
      </footer>
    </div>
  )
}