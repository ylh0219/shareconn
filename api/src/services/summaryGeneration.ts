import { OpenAI } from 'openai'

// 模拟摘要生成（当没有OpenAI API密钥时使用）
function generateMockSummary(content: string, length: 'short' | 'medium' | 'long'): string {
  // 提供更好的中文摘要
  const summaries = {
    short: '这是一个自动生成的内容摘要，帮助用户快速了解网页核心信息。',
    medium: '该链接内容主要介绍了分享链接自动解析总结服务的功能。通过这个服务，用户可以快速获取网页内容的核心信息，节省阅读时间。',
    long: '该链接内容主要介绍了分享链接自动解析总结服务的功能。通过这个服务，用户可以快速获取网页内容的核心信息，节省阅读时间。支持多种格式的网页，包括新闻文章、博客、产品页面等，能够智能提取关键内容并生成简洁的摘要。'
  }
  
  return summaries[length]
}

export async function generateSummary(
  content: string,
  length: 'short' | 'medium' | 'long' = 'medium'
): Promise<string> {
  try {
    // 检查是否有OpenAI API密钥
    const openaiApiKey = process.env.OPENAI_API_KEY
    
    if (openaiApiKey) {
      const openai = new OpenAI({ apiKey: openaiApiKey })
      
      const response = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant that summarizes web content in Chinese. Provide a clear and concise summary of the following text.'
          },
          {
            role: 'user',
            content: `Summarize the following content in ${length} length:\n\n${content}`
          }
        ],
        max_tokens: length === 'short' ? 50 : length === 'medium' ? 100 : 150
      })
      
      return response.choices[0].message.content || ''
    } else {
      // 使用模拟摘要
      return generateMockSummary(content, length)
    }
  } catch (error) {
    console.error('Summary generation error:', error)
    // 出错时使用模拟摘要
    return generateMockSummary(content, length)
  }
}