<script setup lang="ts">
import { GITHUB_LINK } from '@/utils/const'
import NavUser from './NavUser.vue'

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  type SidebarProps,
  SidebarRail,
} from '@/components/ui/sidebar'

const props = defineProps<SidebarProps>()

// This is sample data.
const data = {
  navMain: [
    {
      title: '开始',
      url: '#',
      items: [
        {
          title: '开始新任务',
          url: '#',
          isActive: false,
        },
      ],
    },
    {
      title: '历史任务',
      url: '#',
      items: [

      ],
    },

    {
      title: '系统设置',
      url: '#',
      items: [
        {
          title: 'MCP 管理',
          url: '/mcp',
          isActive: false,
        },
      ],
    },
  ],
}

</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <!-- 图标 -->
      <div class="flex items-center gap-2 h-15">
        <router-link to="/" class="flex items-center gap-2">
          <img src="@/assets/icon.png" alt="logo" class="w-10 h-10">
          <div class="text-lg font-bold">Fast-MM</div>
        </router-link>
      </div>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup v-for="item in data.navMain" :key="item.title">
        <SidebarGroupLabel>{{ item.title }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="childItem in item.items" :key="childItem.title">
              <SidebarMenuButton as-child :is-active="childItem.isActive">
                <router-link :to="childItem.url">{{ childItem.title }}</router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarRail />
    <SidebarFooter>
      <NavUser />
    </SidebarFooter>
  </Sidebar>
</template>