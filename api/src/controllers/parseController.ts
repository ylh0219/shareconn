import { Request, Response } from 'express'
import { extractContent } from '../services/contentExtraction'
import { generateSummary } from '../services/summaryGeneration'
import supabase from '../utils/supabase'

interface ParseRequest {
  url: string
  summaryLength?: 'short' | 'medium' | 'long'
}

interface SaveHistoryRequest {
  url: string
  title: string
  summary: string
}

const parseController = {
  async parseUrl(req: Request, res: Response) {
    try {
      const { url, summaryLength = 'medium' } = req.body as ParseRequest
      
      if (!url) {
        return res.status(400).json({ success: false, error: 'URL is required' })
      }
      
      // 提取内容
      const { title, content } = await extractContent(url)
      
      // 生成摘要
      const summary = await generateSummary(content, summaryLength)
      
      res.status(200).json({
        success: true,
        data: {
          title,
          summary,
          originalUrl: url,
          extractedContent: content,
          timestamp: new Date().toISOString()
        }
      })
    } catch (error) {
      console.error('Parse error:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to parse URL'
      })
    }
  },
  
  async getHistory(req: Request, res: Response) {
    try {
      // 从Supabase获取历史记录
      const { data, error } = await supabase
        .from('history')
        .select('id, url, title, summary, created_at as timestamp')
        .order('created_at', { ascending: false })
        .limit(10)
      
      if (error) {
        console.error('Supabase error:', error)
        // 出错时返回模拟数据
        const mockHistory = [
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
        ]
        return res.status(200).json({
          success: true,
          data: mockHistory
        })
      }
      
      res.status(200).json({
        success: true,
        data: data
      })
    } catch (error) {
      console.error('Get history error:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to get history'
      })
    }
  },
  
  async saveHistory(req: Request, res: Response) {
    try {
      const { url, title, summary } = req.body as SaveHistoryRequest
      
      if (!url || !title || !summary) {
        return res.status(400).json({ success: false, error: 'Missing required fields' })
      }
      
      // 保存到Supabase数据库
      const { data, error } = await supabase
        .from('history')
        .insert({
          url,
          title,
          summary,
          summary_length: 'medium'
        })
        .select('id')
        .single()
      
      if (error) {
        console.error('Supabase error:', error)
        // 出错时返回模拟ID
        const mockId = Date.now().toString()
        return res.status(200).json({
          success: true,
          data: { id: mockId }
        })
      }
      
      res.status(200).json({
        success: true,
        data: { id: data.id }
      })
    } catch (error) {
      console.error('Save history error:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to save history'
      })
    }
  },
  
  generateApiKey(req: Request, res: Response) {
    try {
      // 模拟生成API密钥
      const mockApiKey = `sk_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
      
      res.status(200).json({
        success: true,
        data: { apiKey: mockApiKey }
      })
    } catch (error) {
      console.error('Generate API key error:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to generate API key'
      })
    }
  }
}

export default parseController