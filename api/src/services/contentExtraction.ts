import axios from 'axios'
import * as cheerio from 'cheerio'

export interface ExtractedContent {
  title: string
  content: string
}

export async function extractContent(url: string): Promise<ExtractedContent> {
  try {
    // 确保URL格式正确
    let validUrl = url
    if (!validUrl.startsWith('http://') && !validUrl.startsWith('https://')) {
      validUrl = 'https://' + validUrl
    }
    
    // 获取网页内容
    const response = await axios.get(validUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      },
      timeout: 10000,
      maxRedirects: 5,
      proxy: false // 禁用代理，直接请求目标URL
    })
    
    const html = response.data
    const $ = cheerio.load(html)
    
    // 提取标题
    let title = $('title').text().trim()
    if (!title) {
      title = $('h1').first().text().trim()
    }
    if (!title) {
      title = 'Untitled'
    }
    
    // 提取正文内容
    let content = ''
    
    // 尝试不同的内容选择器
    const contentSelectors = [
      'article',
      '.article-content',
      '.content',
      '.post-content',
      '.entry-content',
      'main',
      'body'
    ]
    
    for (const selector of contentSelectors) {
      const element = $(selector)
      if (element.length > 0) {
        content = element.text().trim()
        if (content.length > 100) {
          break
        }
      }
    }
    
    // 如果仍然没有内容，使用整个页面文本
    if (!content || content.length < 100) {
      content = $('body').text().trim()
    }
    
    // 清理内容
    content = content
      .replace(/\s+/g, ' ') // 替换多个空格为单个空格
      .replace(/\n+/g, '\n') // 替换多个换行为单个换行
      .trim()
    
    return {
      title,
      content
    }
  } catch (error) {
    console.error('Content extraction error:', error)
    // 返回默认值
    return {
      title: 'Error extracting content',
      content: 'Failed to extract content from the URL'
    }
  }
}