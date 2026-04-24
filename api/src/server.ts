import express from 'express'
import cors from 'cors'
import parseController from './controllers/parseController'

const app = express()
const PORT = process.env.PORT || 3001

// 中间件
app.use(cors())
app.use(express.json())

// API路由
app.post('/api/parse', parseController.parseUrl)
app.get('/api/history', parseController.getHistory)
app.post('/api/history/save', parseController.saveHistory)
app.post('/api/api-key/generate', parseController.generateApiKey)

// 健康检查
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' })
})

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})

export default app