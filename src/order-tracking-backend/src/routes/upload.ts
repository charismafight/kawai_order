import express from 'express'
import { uploadSingle } from '../middleware/upload'
import { uploadImage } from '../controllers/uploadController'

const router = express.Router()

// 上传图片
router.post('/', uploadSingle, uploadImage)

export default router