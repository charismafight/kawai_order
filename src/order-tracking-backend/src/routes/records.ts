import express from 'express'
import {
    getRecords,
    getRecord,
    updateRemark,
    deleteRecordById
} from '../controllers/recordsController'

const router = express.Router()

// 获取所有记录
router.get('/', getRecords)

// 获取单条记录
router.get('/:id', getRecord)

// 更新备注
router.put('/:id/remark', updateRemark)

// 删除记录
router.delete('/:id', deleteRecordById)

export default router