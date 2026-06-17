import multer from 'multer'
import path from 'path'
import fs from 'fs'
import { generateRecordId } from '../utils/helpers'

// 确保 uploads 目录存在
const uploadDir = path.join(__dirname, '../../uploads')
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true })
}

// 配置存储
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir)
    },
    filename: (req, file, cb) => {
        // 使用时间戳 + 随机数 + 原始文件名
        const timestamp = Date.now()
        const random = Math.floor(Math.random() * 10000)
        const ext = path.extname(file.originalname)
        const name = `${timestamp}-${random}${ext}`
        cb(null, name)
    }
})

// 文件过滤
const fileFilter = (req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true)
    } else {
        cb(new Error('只支持 JPG, PNG, GIF, WebP 格式') as any, false)
    }
}

// 创建 multer 实例
export const upload = multer({
    storage,
    fileFilter,
    limits: {
        fileSize: 20 * 1024 * 1024
    }
})

// 单文件上传中间件
export const uploadSingle = upload.single('image')