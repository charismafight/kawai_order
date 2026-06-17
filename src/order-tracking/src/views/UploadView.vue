<template>
    <div class="upload-page">
        <!-- 左右两栏布局 -->
        <div class="upload-layout">
            <!-- 左侧：上传区域 -->
            <div class="upload-left">
                <n-card class="upload-card" :bordered="false">
                    <template #header>
                        <div class="card-header">
                            <n-icon :size="24" color="#18a058">
                                <CloudUploadOutline />
                            </n-icon>
                            <span class="card-title">上传图片</span>
                        </div>
                    </template>

                    <n-upload ref="uploadRef" :action="uploadAction" :multiple="false" :accept="'image/*'"
                        :max-size="5 * 1024 * 1024" :default-upload="false" :headers="uploadHeaders" :data="uploadData"
                        @change="handleFileChange">
                        <n-upload-dragger class="upload-dragger">
                            <div class="dragger-content">
                                <n-icon :size="56" color="#18a058" class="upload-icon">
                                    <CloudUploadOutline />
                                </n-icon>
                                <n-text class="upload-text">点击或拖拽图片到此处上传</n-text>
                                <p class="upload-hint">
                                    支持 JPG, PNG, GIF, WebP 格式，单个文件不超过 5MB
                                </p>
                                <n-space class="upload-actions" :size="12">
                                    <n-button type="primary" size="large" round>
                                        <template #icon>
                                            <n-icon>
                                                <FolderOpenOutline />
                                            </n-icon>
                                        </template>
                                        选择文件
                                    </n-button>
                                    <n-button size="large" round ghost>
                                        <template #icon>
                                            <n-icon>
                                                <CameraOutline />
                                            </n-icon>
                                        </template>
                                        拍照上传
                                    </n-button>
                                </n-space>
                            </div>
                        </n-upload-dragger>
                    </n-upload>
                </n-card>
            </div>

            <!-- 右侧：二维码展示区域 -->
            <div class="upload-right">
                <n-card v-if="currentQrCode" class="qrcode-card" :bordered="false" :segmented="true">
                    <template #header>
                        <div class="card-header">
                            <n-icon :size="24" color="#18a058">
                                <QrCodeOutline />
                            </n-icon>
                            <span class="card-title">二维码</span>
                            <n-tag type="success" size="small" class="qrcode-status">已生成</n-tag>
                        </div>
                    </template>

                    <div class="qrcode-content">
                        <div class="qrcode-left">
                            <div class="qrcode-image-wrapper">
                                <img :src="currentQrCode" alt="二维码" class="qrcode-image" />
                            </div>
                        </div>
                        <div class="qrcode-right">
                            <n-descriptions :column="1" size="small" bordered label-placement="left" :label-style="{
                                width: '80px',
                                minWidth: '80px',
                                whiteSpace: 'nowrap',
                                flexShrink: '0'
                            }">
                                <n-descriptions-item label="记录ID">
                                    <n-tag type="success" size="small">{{ currentRecordId }}</n-tag>
                                </n-descriptions-item>
                                <n-descriptions-item label="图片名称">
                                    {{ currentFileName || '未命名' }}
                                </n-descriptions-item>
                                <n-descriptions-item label="图片大小">
                                    {{ currentFileSize || '--' }}
                                </n-descriptions-item>
                                <n-descriptions-item label="生成时间">
                                    {{ currentTime || '刚刚' }}
                                </n-descriptions-item>
                                <n-descriptions-item label="备注">
                                    <n-input v-model:value="currentRemark" placeholder="请输入备注信息（选填）" size="small"
                                        @change="updateRemark" />
                                </n-descriptions-item>
                            </n-descriptions>
                            <n-space class="qrcode-actions" :size="12">
                                <n-button type="primary" size="large" round block @click="downloadQrCode">
                                    <template #icon>
                                        <n-icon>
                                            <DownloadOutline />
                                        </n-icon>
                                    </template>
                                    下载二维码
                                </n-button>
                                <n-button size="large" round block ghost @click="printQrCode">
                                    <template #icon>
                                        <n-icon>
                                            <PrintOutline />
                                        </n-icon>
                                    </template>
                                    打印二维码
                                </n-button>
                            </n-space>
                        </div>
                    </div>
                </n-card>

                <!-- 空状态 -->
                <n-card v-else class="qrcode-card" :bordered="false">
                    <div class="qrcode-empty">
                        <n-icon :size="64" color="#d4d4d4">
                            <QrCodeOutline />
                        </n-icon>
                        <p class="empty-text">上传图片后自动生成二维码</p>
                        <p class="empty-hint">支持 JPG, PNG, GIF, WebP 格式</p>
                    </div>
                </n-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import QRCode from 'qrcode'
import type { UploadFileInfo } from 'naive-ui'
import {
    CloudUploadOutline,
    FolderOpenOutline,
    CameraOutline,
    QrCodeOutline,
    DownloadOutline,
    PrintOutline,
} from '@vicons/ionicons5'

const message = useMessage()

// 响应式数据
const uploadRef = ref()
const currentQrCode = ref<string>('')
const currentRecordId = ref<string>('')
const currentFileName = ref<string>('')
const currentFileSize = ref<string>('')
const currentTime = ref<string>('')
const currentRemark = ref<string>('')
const currentImageUrl = ref<string>('')

// API 基础地址
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

// 上传配置 - 使用后端 API
const uploadAction = `${API_BASE}/upload`
const uploadHeaders = {}
const uploadData = {}

// 保存当前记录ID（用于更新备注）
let currentRecordIdValue = ''

// 更新备注 - 调用后端 API
const updateRemark = async () => {
    if (!currentRecordIdValue) {
        message.warning('请先上传图片')
        return
    }

    try {
        const response = await fetch(`${API_BASE}/records/${currentRecordIdValue}/remark`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ remark: currentRemark.value }),
        })

        const result = await response.json()

        if (result.success) {
            message.success('备注已更新')
        } else {
            message.error(result.error || '更新失败')
        }
    } catch (error) {
        console.error('更新备注失败:', error)
        message.error('更新备注失败，请重试')
    }
}

// 处理文件选择变化
const handleFileChange = async (data: { file: UploadFileInfo; fileList: UploadFileInfo[]; event: Event }) => {
    console.log('文件变化:', data)
    const file = data.file

    // 验证文件大小
    const maxSize = 5 * 1024 * 1024
    if (file.file?.size && file.file.size > maxSize) {
        message.error('文件大小不能超过 5MB')
        return
    }

    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (file.file?.type && !allowedTypes.includes(file.file.type)) {
        message.error('只支持 JPG, PNG, GIF, WebP 格式')
        return
    }

    // 上传到后端
    await uploadToServer(file)
}

// 上传到后端服务器
const uploadToServer = async (file: UploadFileInfo) => {
    const formData = new FormData()
    formData.append('image', file.file as Blob)
    formData.append('remark', currentRemark.value || '')

    message.loading('正在上传...')

    try {
        const response = await fetch(uploadAction, {
            method: 'POST',
            body: formData,
        })

        const result = await response.json()

        if (!result.success) {
            message.error(result.error || '上传失败')
            return
        }

        const data = result.data
        const imageUrl = data.imageUrl

        // 生成二维码（使用记录ID作为数据）
        const qrOptions = {
            width: 200,
            margin: 2,
            color: {
                dark: '#000000',
                light: '#ffffff'
            }
        }

        const qrCodeDataUrl = await QRCode.toDataURL(imageUrl, qrOptions)
        const beijingTime = new Date().toLocaleString('zh-CN', {
            timeZone: 'Asia/Shanghai'
        })

        // 更新显示
        currentQrCode.value = qrCodeDataUrl
        currentRecordId.value = data.id
        currentFileName.value = data.fileName
        currentFileSize.value = data.fileSize ? (data.fileSize / 1024 / 1024).toFixed(2) + ' MB' : '--'
        currentTime.value = beijingTime
        currentImageUrl.value = data.imageUrl || ''
        currentRecordIdValue = data.id

        // 如果后端返回了备注，更新备注
        if (data.remark) {
            currentRemark.value = data.remark
        }

        message.success('上传成功，二维码已生成！')
    } catch (error) {
        console.error('上传失败:', error)
        message.error('上传失败，请检查网络连接')
    }
}

// 下载二维码
const downloadQrCode = (): void => {
    if (!currentQrCode.value) return

    const link = document.createElement('a')
    link.download = `qrcode-${currentRecordId.value}.png`
    link.href = currentQrCode.value
    link.click()
    message.success('二维码下载成功')
}

// 打印二维码
const printQrCode = (): void => {
    if (!currentQrCode.value) return

    const printWindow = window.open('', '_blank')
    if (!printWindow) {
        message.error('请允许弹出窗口')
        return
    }

    printWindow.document.write(`
    <html>
      <head>
        <title>二维码 - ${currentRecordId.value}</title>
        <style>
          body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: white; font-family: Arial, sans-serif; }
          .container { text-align: center; }
          img { max-width: 300px; border: 1px solid #ddd; border-radius: 8px; padding: 16px; }
          .info { margin-top: 16px; }
          .id { font-size: 18px; font-weight: bold; color: #18a058; }
          .name { color: #666; }
          .remark { color: #999; font-size: 14px; margin-top: 8px; }
        </style>
      </head>
      <body>
        <div class="container">
          <img src="${currentQrCode.value}" alt="二维码" />
          <div class="info">
            <div class="id">${currentRecordId.value}</div>
            <div class="name">${currentFileName.value}</div>
            ${currentRemark.value ? `<div class="remark">备注：${currentRemark.value}</div>` : ''}
          </div>
        </div>
        <script>
          // 等待图片加载完成后自动打印
          window.onload = function() {
            setTimeout(function() {
              window.print();
            }, 500);
          };
        <\/script>
      </body>
    </html>
  `)
    printWindow.document.close()
}
</script>

<style scoped>
/* ... 样式保持不变 ... */
.upload-page {
    width: 100%;
}

.upload-layout {
    display: grid;
    grid-template-columns: 0.7fr 1.3fr;
    gap: 24px;
    align-items: stretch;
}

.upload-left {
    min-height: 400px;
}

.upload-right {
    min-height: 400px;
}

.upload-card {
    background: white;
    height: 100%;
}

.upload-card :deep(.n-card__content) {
    height: calc(100% - 56px);
    padding: 0;
}

.upload-dragger {
    min-height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.dragger-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 40px 20px;
    width: 100%;
}

.upload-icon {
    animation: float 3s ease-in-out infinite;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-8px);
    }
}

.upload-text {
    font-size: 18px;
    font-weight: 500;
    color: #1a1a1a;
}

.upload-hint {
    margin: 0;
    color: #999;
    font-size: 14px;
}

.upload-actions {
    margin-top: 8px;
}

.qrcode-card {
    background: white;
    height: 100%;
}

.qrcode-card :deep(.n-card__content) {
    height: calc(100% - 56px);
    padding: 16px 24px;
    display: flex;
    align-items: center;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.card-title {
    font-size: 18px;
    font-weight: 600;
}

.qrcode-status {
    margin-left: auto;
}

.qrcode-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    width: 100%;
}

.qrcode-left {
    display: flex;
    justify-content: center;
    align-items: center;
}

.qrcode-image-wrapper {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 2px dashed #e5e5e5;
}

.qrcode-image {
    width: 180px;
    height: 180px;
    display: block;
}

.qrcode-right {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
}

.qrcode-actions {
    margin-top: 4px;
}

.qrcode-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    width: 100%;
    height: 100%;
}

.empty-text {
    color: #999;
    font-size: 16px;
    margin-top: 16px;
}

.empty-hint {
    color: #ccc;
    font-size: 14px;
    margin-top: 4px;
}

@media (max-width: 1024px) {
    .upload-layout {
        grid-template-columns: 1fr;
        gap: 16px;
    }

    .upload-left {
        min-height: 300px;
    }

    .upload-right {
        min-height: 350px;
    }

    .qrcode-content {
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .qrcode-image {
        width: 160px;
        height: 160px;
    }
}

@media (max-width: 768px) {
    .upload-left {
        min-height: 250px;
    }

    .upload-right {
        min-height: 400px;
    }

    .upload-dragger {
        min-height: 200px;
    }

    .dragger-content {
        padding: 24px 16px;
        gap: 12px;
    }

    .upload-text {
        font-size: 16px;
    }

    .upload-hint {
        font-size: 12px;
    }

    .upload-actions {
        flex-direction: column;
        width: 100%;
        gap: 8px !important;
    }

    .upload-actions .n-button {
        width: 100%;
        justify-content: center;
    }

    .qrcode-card :deep(.n-card__content) {
        padding: 12px 16px;
        display: block;
    }

    .qrcode-content {
        grid-template-columns: 1fr;
        gap: 16px;
    }

    .qrcode-image {
        width: 160px;
        height: 160px;
    }

    .qrcode-left {
        order: 1;
    }

    .qrcode-right {
        order: 2;
    }

    .qrcode-actions {
        flex-direction: column;
        width: 100%;
    }

    .qrcode-actions .n-button {
        width: 100%;
    }

    .qrcode-empty {
        padding: 20px 16px;
    }

    .empty-text {
        font-size: 14px;
    }

    .card-title {
        font-size: 16px;
    }
}

@media (max-width: 480px) {
    .qrcode-image {
        width: 140px;
        height: 140px;
    }

    .upload-dragger {
        min-height: 160px;
    }

    .dragger-content {
        padding: 16px 12px;
    }

    .upload-icon {
        font-size: 40px !important;
    }

    .upload-text {
        font-size: 14px;
    }

    .qrcode-card :deep(.n-card__content) {
        padding: 8px 12px;
    }
}
</style>