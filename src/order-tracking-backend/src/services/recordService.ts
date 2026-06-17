import db from '../database/db'
import { generateRecordId } from '../utils/helpers'
import fs from 'fs'

export interface Record {
    id: number
    record_id: string
    file_name: string
    file_path: string
    file_size: number
    remark: string
    created_at: string
    updated_at: string
}

export interface CreateRecordData {
    fileName: string
    filePath: string
    fileSize: number
    remark?: string
}

// 获取北京时间字符串
const getBeijingTime = (): string => {
    const now = new Date()
    // 转换为北京时间（UTC+8）
    const beijingTime = new Date(now.getTime() + 8 * 60 * 60 * 1000)
    return beijingTime.toISOString().replace('T', ' ').slice(0, 19)
}

// 创建记录
export const createRecord = (data: CreateRecordData): Record => {
    const recordId = generateRecordId()
    const now = getBeijingTime()  // ✅ 使用北京时间

    const stmt = db.prepare(`
    INSERT INTO records (record_id, file_name, file_path, file_size, remark, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `)

    const info = stmt.run(
        recordId,
        data.fileName,
        data.filePath,
        data.fileSize,
        data.remark || '',
        now,
        now
    )

    return getRecordById(info.lastInsertRowid as number) as Record
}

// 获取所有记录
export const getAllRecords = (): Record[] => {
    const stmt = db.prepare('SELECT * FROM records ORDER BY created_at DESC')
    return stmt.all() as Record[]
}

// 根据 ID 获取记录
export const getRecordById = (id: number): Record | null => {
    const stmt = db.prepare('SELECT * FROM records WHERE id = ?')
    return stmt.get(id) as Record || null
}

// 根据 record_id 获取记录
export const getRecordByRecordId = (recordId: string): Record | null => {
    const stmt = db.prepare('SELECT * FROM records WHERE record_id = ?')
    return stmt.get(recordId) as Record || null
}

// 更新记录备注
export const updateRecordRemark = (recordId: string, remark: string): Record | null => {
    const now = getBeijingTime()  // ✅ 使用北京时间
    const stmt = db.prepare(`
    UPDATE records SET remark = ?, updated_at = ?
    WHERE record_id = ?
  `)
    stmt.run(remark, now, recordId)
    return getRecordByRecordId(recordId)
}

// 删除记录
export const deleteRecord = (recordId: string): boolean => {
    const record = getRecordByRecordId(recordId)
    if (!record) return false

    try {
        if (fs.existsSync(record.file_path)) {
            fs.unlinkSync(record.file_path)
        }
    } catch (error) {
        console.error('删除文件失败:', error)
    }

    const stmt = db.prepare('DELETE FROM records WHERE record_id = ?')
    const result = stmt.run(recordId)
    return result.changes > 0
}

// 获取记录总数
export const getRecordsCount = (): number => {
    const stmt = db.prepare('SELECT COUNT(*) as count FROM records')
    const result = stmt.get() as { count: number }
    return result.count
}