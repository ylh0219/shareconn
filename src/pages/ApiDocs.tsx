import { useState } from 'react'

export default function ApiDocs() {
  const [activeTab, setActiveTab] = useState('usage')

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            API文档
          </h1>
          <p className="mt-2 text-gray-600">
            了解如何使用我们的API来自动解析和总结分享链接
          </p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('usage')}
                className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'usage' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                使用指南
              </button>
              <button
                onClick={() => setActiveTab('examples')}
                className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'examples' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                代码示例
              </button>
              <button
                onClick={() => setActiveTab('limits')}
                className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'limits' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                速率限制
              </button>
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'usage' && (
              <div className="space-y-6">
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    端点说明
                  </h2>
                  
                  <div className="space-y-4">
                    <div className="border border-gray-100 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">
                        POST /api/parse
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">
                        解析并总结URL
                      </p>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">请求体</h4>
                        <pre className="text-xs font-mono bg-white p-2 rounded border border-gray-200">
                          {
`{
  "url": "https://example.com",
  "summaryLength": "medium"
}`
                          }
                        </pre>
                      </div>
                      <div className="bg-gray-50 p-3 rounded-lg mt-3">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">响应</h4>
                        <pre className="text-xs font-mono bg-white p-2 rounded border border-gray-200">
                          {
`{
  "success": true,
  "data": {
    "title": "Example Domain",
    "summary": "This is an example domain.",
    "originalUrl": "https://example.com",
    "extractedContent": "...",
    "timestamp": "2026-04-24T09:24:11.019Z"
  }
}`
                          }
                        </pre>
                      </div>
                    </div>
                    
                    <div className="border border-gray-100 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">
                        GET /api/history
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">
                        获取用户的解析历史
                      </p>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">响应</h4>
                        <pre className="text-xs font-mono bg-white p-2 rounded border border-gray-200">
                          {
`{
  "success": true,
  "data": [
    {
      "id": "1",
      "url": "https://example.com",
      "title": "Example Domain",
      "summary": "This is an example domain.",
      "timestamp": "2026-04-24T09:24:11.019Z"
    }
  ]
}`
                          }
                        </pre>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            )}
            
            {activeTab === 'examples' && (
              <div className="space-y-6">
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    代码示例
                  </h2>
                  
                  <div className="space-y-4">
                    <div className="border border-gray-100 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">
                        JavaScript (Fetch)
                      </h3>
                      <pre className="text-xs font-mono bg-white p-3 rounded border border-gray-200 overflow-x-auto">
                        {
`async function parseUrl(url) {
  const response = await fetch('http://localhost:3001/api/parse', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url })
  });
  const data = await response.json();
  return data;
}

// 使用示例
parseUrl('https://example.com')
  .then(result => console.log(result))
  .catch(error => console.error(error));`
                        }
                      </pre>
                    </div>
                    
                    <div className="border border-gray-100 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">
                        Python (requests)
                      </h3>
                      <pre className="text-xs font-mono bg-white p-3 rounded border border-gray-200 overflow-x-auto">
                        {
`import requests

def parse_url(url):
    response = requests.post(
        'http://localhost:3001/api/parse',
        json={'url': url}
    )
    return response.json()

# 使用示例
result = parse_url('https://example.com')
print(result)`
                        }
                      </pre>
                    </div>
                  </div>
                </section>
              </div>
            )}
            
            {activeTab === 'limits' && (
              <div className="space-y-6">
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    速率限制
                  </h2>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            套餐
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            免费调用次数/天
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            价格
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            免费版
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            100
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ¥0
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            基础版
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            1000
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ¥99/月
                          </td>
                        </tr>
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            高级版
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            10000
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ¥499/月
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>
            )}
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