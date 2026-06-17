import Database from 'better-sqlite3'
import path from 'path'
import fs from 'fs'

// 确保 data 目录存在
const dataDir = path.join(__dirname, '../../data')
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true })
}

const dbPath = path.join(dataDir, 'records.db')
const db = new Database(dbPath)

// 创建表
db.exec(`
  CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id VARCHAR(20) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    remark TEXT DEFAULT '',
    created_at DATETIME,
    updated_at DATETIME
  );

  CREATE INDEX IF NOT EXISTS idx_record_id ON records(record_id);
  CREATE INDEX IF NOT EXISTS idx_created_at ON records(created_at);
`)

// ✅ 使用类型断言导出
export default db