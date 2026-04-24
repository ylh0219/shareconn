import { OpenAI } from 'openai'

// 模拟摘要生成（当没有OpenAI API密钥时使用）
function generateMockSummary(content: string, length: 'short' | 'medium' | 'long'): string {
  const sentences = content.split('. ').filter(s => s.trim())
  let summaryLength = 2
  
  switch (length) {
    case 'short':
      summaryLength = 1
      break
    case 'medium':
      summaryLength = 2
      break
    case 'long':
      summaryLength = 3
      break
  }
  
  const summarySentences = sentences.slice(0, summaryLength)
  return summarySentences.join('. ') + '.'
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