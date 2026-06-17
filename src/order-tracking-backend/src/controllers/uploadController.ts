import { Request, Response } from 'express'
import { createRecord } from '../services/recordService'
import path from 'path'

export const uploadImage = async (req: Request, res: Response) => {
    try {
        // 检查文件是否存在
        if (!req.file) {
            return res.status(400).json({ error: '请选择要上传的图片' })
        }

        const file = req.file
        const remark = req.body.remark || ''

        // 保存记录到数据库
        const record = createRecord({
            fileName: file.originalname,
            filePath: file.path,
            fileSize: file.size,
            remark: remark
        })

        // 构造图片 URL（用于前端显示）
        const baseUrl = `${req.protocol}://${req.get('host')}`
        const imageUrl = `${baseUrl}/uploads/${path.basename(file.path)}`

        // 返回响应
        res.json({
            success: true,
            data: {
                id: record.record_id,
                fileName: record.file_name,
                fileSize: record.file_size,
                uploadTime: record.created_at,
                remark: record.remark,
                imageUrl: imageUrl
            }
        })
    } catch (error) {
        console.error('上传失败:', error)
        res.status(500).json({ error: '上传失败，请重试' })
    }
}