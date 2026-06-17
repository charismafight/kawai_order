<template>
  <n-config-provider>
    <n-message-provider>
      <n-dialog-provider>
        <n-layout class="app-layout">
          <!-- 头部导航 -->
          <n-layout-header bordered class="app-header">
            <div class="header-content">
              <div class="header-left">
                <span class="header-title"></span>
              </div>
              <div class="header-nav">
                <n-menu v-model:value="activeKey" mode="horizontal" :options="menuOptions"
                  @update:value="handleMenuChange" />
              </div>
            </div>
          </n-layout-header>

          <!-- 内容区 -->
          <n-layout-content class="app-content">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CameraOutline, DocumentTextOutline } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import type { MenuOption } from 'naive-ui'

const router = useRouter()
const route = useRoute()

const activeKey = ref<string>(route.name as string || 'Upload')

const menuOptions: MenuOption[] = [
  {
    label: '上传图片',
    key: 'Upload',
    icon: () => h(NIcon, null, { default: () => h(CameraOutline) })
  },
  {
    label: '上传记录',
    key: 'Records',
    icon: () => h(NIcon, null, { default: () => h(DocumentTextOutline) })
  }
]

const handleMenuChange = (key: string) => {
  router.push({ name: key })
}

// 监听路由变化，更新菜单高亮
onMounted(() => {
  activeKey.value = route.name as string || 'Upload'
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: white;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.header-nav {
  flex: 1;
  margin-left: 48px;
}

.app-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .header-content {
    height: 56px;
  }

  .header-title {
    font-size: 16px;
  }

  .header-nav {
    margin-left: 16px;
  }

  .app-content {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .header-title {
    display: none;
  }

  .header-nav {
    margin-left: 0;
  }
}
</style>