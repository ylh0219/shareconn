import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { HistoryItem } from '../components/HistoryList'

export default function Dashboard() {
  const navigate = useNavigate()
  const [savedSummaries, setSavedSummaries] = useState<HistoryItem[]>([
    {
      id: '1',
      url: 'https://example.com/article1',
      title: '示例文章1',
      summary: '这是示例文章1的摘要',
      timestamp: new Date().toISOString()
    },
    {
      id: '2',
      url: 'https://example.com/article2',
      title: '示例文章2',
      summary: '这是示例文章2的摘要',
      timestamp: new Date().toISOString()
    }
  ])

  const handleLogout = () => {
    // 模拟登出
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              仪表盘
            </h1>
            <button
              onClick={handleLogout}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors"
            >
              登出
            </button>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <section className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                保存的摘要
              </h2>
              
              {savedSummaries.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">暂无保存的摘要</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {savedSummaries.map((item) => (
                    <div key={item.id} className="border border-gray-100 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start">
                        <h3 className="font-medium text-gray-900">{item.title}</h3>
                        <span className="text-xs text-gray-500">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">{item.summary}</p>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-600 text-sm font-medium mt-3 inline-block"
                      >
                        查看原文
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
          
          <div className="lg:col-span-1 space-y-6">
            <section className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                个人设置
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    默认摘要长度
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="short">简短</option>
                    <option value="medium" selected>中等</option>
                    <option value="long">详细</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    主题
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="light" selected>浅色</option>
                    <option value="dark">深色</option>
                  </select>
                </div>
              </div>
            </section>
            
            <section className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                API密钥管理
              </h2>
              
              <div className="space-y-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">当前API密钥</p>
                  <p className="text-sm font-mono bg-white p-2 rounded border border-gray-200">
                    sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                  </p>
                </div>
                
                <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  生成新密钥
                </button>
              </div>
            </section>
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