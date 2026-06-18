import { Request, Response } from 'express'
import {
    getAllRecords,
    getRecordByRecordId,
    updateRecordRemark,
    deleteRecord,
    getRecordsCount
} from '../services/recordService'
import path from 'path'

// 获取所有记录
export const getRecords = (req: Request, res: Response) => {
    try {
        const records = getAllRecords()
        const count = getRecordsCount()

        // 转换数据格式，添加图片URL
        const port = 16666
        const baseUrl = `${req.protocol}://${req.get('host')}:${port}`
        const formattedRecords = records.map(record => ({
            id: record.record_id,
            fileName: record.file_name,
            fileSize: record.file_size,
            uploadTime: record.created_at,
            remark: record.remark,
            imageUrl: `${baseUrl}/uploads/${path.basename(record.file_path)}`
        }))

        res.json({
            success: true,
            data: formattedRecords,
            total: count
        })
    } catch (error) {
        console.error('获取记录失败:', error)
        res.status(500).json({ error: '获取记录失败' })
    }
}

// 获取单条记录
export const getRecord = (req: Request, res: Response) => {
    try {
        // ✅ 修复：确保 id 是 string 类型
        const id = req.params.id as string

        if (!id) {
            return res.status(400).json({ error: '记录ID不能为空' })
        }

        const record = getRecordByRecordId(id)

        if (!record) {
            return res.status(404).json({ error: '记录不存在' })
        }

        const baseUrl = `${req.protocol}://${req.get('host')}`
        res.json({
            success: true,
            data: {
                id: record.record_id,
                fileName: record.file_name,
                fileSize: record.file_size,
                uploadTime: record.created_at,
                remark: record.remark,
                imageUrl: `${baseUrl}/uploads/${path.basename(record.file_path)}`
            }
        })
    } catch (error) {
        console.error('获取记录失败:', error)
        res.status(500).json({ error: '获取记录失败' })
    }
}

// 更新记录备注
export const updateRemark = (req: Request, res: Response) => {
    try {
        // ✅ 修复：确保 id 是 string 类型
        const id = req.params.id as string
        const { remark } = req.body

        if (!id) {
            return res.status(400).json({ error: '记录ID不能为空' })
        }

        const record = updateRecordRemark(id, remark || '')

        if (!record) {
            return res.status(404).json({ error: '记录不存在' })
        }

        res.json({
            success: true,
            data: {
                id: record.record_id,
                remark: record.remark,
                updatedAt: record.updated_at
            }
        })
    } catch (error) {
        console.error('更新备注失败:', error)
        res.status(500).json({ error: '更新备注失败' })
    }
}

// 删除记录
export const deleteRecordById = (req: Request, res: Response) => {
    try {
        // ✅ 修复：确保 id 是 string 类型
        const id = req.params.id as string

        if (!id) {
            return res.status(400).json({ error: '记录ID不能为空' })
        }

        const success = deleteRecord(id)

        if (!success) {
            return res.status(404).json({ error: '记录不存在' })
        }

        res.json({
            success: true,
            message: '记录已删除'
        })
    } catch (error) {
        console.error('删除记录失败:', error)
        res.status(500).json({ error: '删除记录失败' })
    }
}