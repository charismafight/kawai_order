import express from 'express'
import cors from 'cors'
import path from 'path'
import uploadRoutes from './routes/upload'
import recordsRoutes from './routes/records'

const app = express()
const PORT = process.env.PORT || 3000

// 中间件
app.use(cors({
    origin: 'http://111.4.8.192:5173',
    credentials: true
}))
app.use(express.json({ limit: '20mb' }))
app.use(express.urlencoded({ extended: true }))

// 静态文件服务（让前端可以访问上传的图片）
app.use('/uploads', express.static(path.join(__dirname, '../uploads')))

// 路由
app.use('/api/upload', uploadRoutes)
app.use('/api/records', recordsRoutes)

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// 错误处理中间件
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error('服务器错误:', err)
    res.status(500).json({ error: '服务器内部错误' })
})

// 启动服务器
app.listen(PORT, () => {
    console.log(`🚀 服务器已启动: http://localhost:${PORT}`)
    console.log(`📁 上传目录: ${path.join(__dirname, '../uploads')}`)
    console.log(`📊 数据库: ${path.join(__dirname, '../data/records.db')}`)
})