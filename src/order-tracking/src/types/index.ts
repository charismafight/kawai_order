// 上传记录类型
export interface UploadRecord {
    id: string | number
    fileName: string
    fileSize: number // 字节
    fileType: string
    uploadTime: string
    qrCode: string
    imageUrl: string
    status?: 'uploading' | 'success' | 'error'
}

// 上传响应类型（根据实际后端调整）
export interface UploadResponse {
    id: string
    url: string
    fileName: string
    size: number
    uploadTime: string
}

// 二维码生成参数
export interface QRCodeOptions {
    width?: number
    margin?: number
    color?: {
        dark?: string
        light?: string
    }
}

// 表格列配置类型
export interface TableColumn {
    title: string
    key: string
    width?: number
    ellipsis?: boolean
    render?: (row: UploadRecord) => any
}