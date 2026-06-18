<template>
    <div class="records-page">
        <n-card class="records-card" :bordered="false">
            <template #header>
                <div class="card-header">
                    <div class="header-left">
                        <n-icon :size="24" color="#18a058">
                            <DocumentTextOutline />
                        </n-icon>
                        <span class="card-title">上传记录</span>
                        <n-tag type="info" size="small">{{ records.length }} 条记录</n-tag>
                    </div>
                    <div class="header-right">
                        <n-button size="small" ghost @click="loadRecords">
                            <template #icon>
                                <n-icon>
                                    <RefreshOutline />
                                </n-icon>
                            </template>
                            刷新
                        </n-button>
                    </div>
                </div>
            </template>

            <!-- 搜索 -->
            <div class="search-bar">
                <n-input v-model:value="searchKeyword" placeholder="搜索图片名称..." clearable size="large">
                    <template #prefix>
                        <n-icon>
                            <SearchOutline />
                        </n-icon>
                    </template>
                </n-input>
            </div>

            <!-- 记录列表 -->
            <n-data-table :columns="columns" :data="filteredRecords" :bordered="true" :single-line="false"
                :loading="loading" size="medium" class="records-table" :pagination="pagination">
                <template #empty>
                    <div class="empty-state">
                        <n-icon :size="48" color="#d4d4d4">
                            <DocumentTextOutline />
                        </n-icon>
                        <p>暂无上传记录</p>
                        <n-button type="primary" size="small" @click="goToUpload">
                            去上传图片
                        </n-button>
                    </div>
                </template>
            </n-data-table>
        </n-card>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
    DocumentTextOutline,
    RefreshOutline,
    SearchOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

// API 基础地址
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

// 数据
const records = ref<any[]>([])
const searchKeyword = ref<string>('')
const loading = ref<boolean>(false)

// 分页配置
const pagination = {
    pageSize: 10,
    showSizePicker: true,
    pageSizes: [10, 20, 50, 100],
}

// 从后端加载记录
const loadRecords = async () => {
    loading.value = true
    try {
        const response = await fetch(`${API_BASE}/records`)
        const result = await response.json()

        if (result.success) {
            records.value = result.data || []
        } else {
            message.error(result.error || '加载记录失败')
        }
    } catch (error) {
        console.error('加载记录失败:', error)
        message.error('加载记录失败，请检查网络连接')
    } finally {
        loading.value = false
    }
}

// 搜索过滤
const filteredRecords = computed(() => {
    if (!searchKeyword.value) {
        return records.value
    }
    const keyword = searchKeyword.value.toLowerCase()
    return records.value.filter((record: any) =>
        record.fileName.toLowerCase().includes(keyword)
    )
})

// 查看实际上传的图片
const viewImage = (record: any) => {
    const imageUrl = record.imageUrl
    if (!imageUrl) {
        message.warning('该记录没有图片')
        return
    }
    dialog.info({
        title: `图片预览 - ${record.fileName}`,
        content: () => h('div', { style: 'text-align: center;' }, [
            h('img', {
                src: imageUrl,
                style: 'max-width: 100%; max-height: 500px; border-radius: 8px;',
                onError: () => {
                    message.error('图片加载失败')
                }
            }),
            h('p', { style: 'margin-top: 12px; color: #999; font-size: 14px;' }, `ID: ${record.id}`),
            record.remark ? h('p', { style: 'color: #999; font-size: 14px;' }, `备注: ${record.remark}`) : null
        ]),
        positiveText: '关闭'
    })
}

// 查看二维码
const viewQrCode = (record: any) => {
    const imageUrl = record.imageUrl || `${API_BASE}/records/${record.id}/image`

    import('qrcode').then((QRCode) => {
        QRCode.toDataURL(imageUrl, {
            width: 200,
            margin: 2,
        }).then((qrCodeDataUrl: string) => {
            dialog.info({
                title: `二维码 - ${record.id}`,
                content: () => h('div', { style: 'text-align: center;' }, [
                    h('img', { src: qrCodeDataUrl, style: 'max-width: 200px;' }),
                    h('p', { style: 'margin-top: 12px;' }, `图片: ${record.fileName}`),
                    record.remark ? h('p', { style: 'color: #999; font-size: 14px;' }, `备注: ${record.remark}`) : null
                ]),
                positiveText: '关闭'
            })
        })
    })
}

// 编辑备注
const editRemark = (record: any) => {
    const currentRemark = record.remark || ''
    const newRemark = prompt(`编辑备注 - ${record.fileName}`, currentRemark)

    if (newRemark === null) return // 用户点击取消

    const remark = newRemark.trim()
    if (remark === currentRemark) {
        message.info('备注未修改')
        return
    }

    fetch(`${API_BASE}/records/${record.id}/remark`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ remark }),
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                message.success('备注已更新')
                loadRecords()
            } else {
                message.error(result.error || '更新失败')
            }
        })
        .catch(error => {
            console.error('更新备注失败:', error)
            message.error('更新失败，请重试')
        })
}

// 删除记录
const deleteRecord = (id: string) => {
    dialog.warning({
        title: '确认删除',
        content: '确定要删除这条记录吗？',
        positiveText: '删除',
        negativeText: '取消',
        onPositiveClick: async () => {
            try {
                const response = await fetch(`${API_BASE}/records/${id}`, {
                    method: 'DELETE',
                })
                const result = await response.json()

                if (result.success) {
                    message.success('记录已删除')
                    await loadRecords()
                } else {
                    message.error(result.error || '删除失败')
                }
            } catch (error) {
                console.error('删除失败:', error)
                message.error('删除失败，请重试')
            }
        }
    })
}

// 跳转到上传页
const goToUpload = () => {
    router.push('/upload')
}

const columns = computed<DataTableColumns>(() => [
    {
        title: 'ID',
        key: 'id',
        width: 150,
        ellipsis: true,
    },
    {
        title: '图片名称',
        key: 'fileName',
        ellipsis: true,
    },
    {
        title: '备注',
        key: 'remark',
        width: 200,
        ellipsis: true,
        render: (row: any) => {
            return row.remark || '-'
        }
    },
    {
        title: '大小',
        key: 'fileSize',
        width: 120,
        render: (row: any) => {
            return (row.fileSize / 1024 / 1024).toFixed(2) + ' MB'
        }
    },
    {
        title: '上传时间',
        key: 'uploadTime',
        width: 180,
    },
    {
        title: '二维码',
        key: 'qrcode',
        width: 120,
        render: (row: any) => {
            return h('div', {
                style: 'cursor: pointer; display: flex; justify-content: center; align-items: center;',
                onClick: () => viewQrCode(row)
            }, [
                h('img', {
                    src: row.qrCode || '',
                    style: 'width: 40px; height: 40px; border: 1px solid #e5e5e5; border-radius: 4px; padding: 4px;',
                    onError: (e: Event) => {
                        import('qrcode').then((QRCode) => {
                            QRCode.toDataURL(row.imageUrl || row.id, {
                                width: 80,
                                margin: 1,
                            }).then((qrCodeDataUrl: string) => {
                                ; (e.target as HTMLImageElement).src = qrCodeDataUrl
                            })
                        })
                    }
                })
            ])
        }
    },
    {
        title: '操作',
        key: 'actions',
        width: 120,
        render: (row: any) => {
            return h('div', { style: 'display: flex; gap: 8px; align-items: center;' }, [
                // 🔍 查看图片
                h(
                    'button',
                    {
                        onClick: () => viewImage(row),
                        title: '查看图片',
                        style: 'background: transparent; border: none; cursor: pointer; font-size: 18px;  border-radius: 6px; transition: all 0.25s ease;',
                        onMouseenter: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = '#e6f0ff'
                            el.style.transform = 'scale(1.15)'
                        },
                        onMouseleave: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = 'transparent'
                            el.style.transform = 'scale(1)'
                        }
                    },
                    { default: () => '🔍' }
                ),
                // ✏️ 编辑备注
                h(
                    'button',
                    {
                        onClick: () => editRemark(row),
                        title: '编辑备注',
                        style: 'background: transparent; border: none; cursor: pointer; font-size: 18px;  border-radius: 6px; transition: all 0.25s ease;',
                        onMouseenter: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = '#fff3e0'
                            el.style.transform = 'scale(1.15)'
                        },
                        onMouseleave: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = 'transparent'
                            el.style.transform = 'scale(1)'
                        }
                    },
                    { default: () => '✏️' }
                ),
                // ❌ 删除（红色 ×）
                h(
                    'button',
                    {
                        onClick: () => deleteRecord(row.id),
                        title: '删除记录',
                        style: 'background: transparent; border: none; cursor: pointer; font-size: 22px;  border-radius: 6px; transition: all 0.25s ease; color: #ff4d4f; font-weight: bold;',
                        onMouseenter: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = '#fde8e8'
                            el.style.transform = 'scale(1.2)'
                        },
                        onMouseleave: (e: MouseEvent) => {
                            const el = e.target as HTMLElement
                            el.style.background = 'transparent'
                            el.style.transform = 'scale(1)'
                        }
                    },
                    { default: () => '✕' }
                )
            ])
        }
    }
])

// 组件挂载时加载数据
onMounted(() => {
    loadRecords()
})
</script>

<style scoped>
.records-page {
    width: 100%;
}

.records-card {
    background: white;
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.header-right {
    display: flex;
    gap: 8px;
}

.card-title {
    font-size: 18px;
    font-weight: 600;
}

.search-bar {
    margin-bottom: 20px;
}

.records-table {
    margin-top: 8px;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
}

.empty-state p {
    color: #999;
    margin: 12px 0;
}

@media (max-width: 768px) {
    .card-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .header-right {
        width: 100%;
        justify-content: flex-end;
    }
}

@media (max-width: 480px) {
    .card-title {
        font-size: 16px;
    }
}
</style>