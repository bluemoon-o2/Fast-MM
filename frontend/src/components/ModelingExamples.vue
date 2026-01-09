<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { exampleAPI, getExamplesList } from '@/apis/commonApi'

// UI Components
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Input } from '@/components/ui/input'
import { Database, FileText, TrendingUp, Activity, Image as ImageIcon, MessageSquare, Search } from 'lucide-vue-next'

// Images
import huashuCupC from '@/assets/example/华数杯2023年C题.png'
import wuyiCupC from '@/assets/example/2025五一杯C题.png'
import mcmCupC from '@/assets/example/2024高教杯C题.png'

interface ModelingExample {
  id: number | string
  title: string
  source: string
  description: string
  tags: string[]
  image?: string
  icon?: any
  datasetInfo?: string
}

const router = useRouter()
const isLoading = ref(false)
const mmbenchExamples = ref<ModelingExample[]>([])
const searchQuery = ref('')

const classicExamples: ModelingExample[] = [
  {
    id: 1,
    title: "母亲身心健康对婴儿成长的影响",
    source: "2023华数杯C题",
    description: "通过母亲的身心健康数据，建立预测模型分析其对婴儿成长的影响。",
    tags: ["分类问题", "医疗健康"],
    image: huashuCupC
  },
  {
    id: 2,
    title: "社交媒体平台用户分析",
    source: "2025五一杯C题",
    description: "分析社交媒体平台用户行为特征，构建精准的用户画像模型。",
    tags: ["用户画像", "社交网络"],
    image: wuyiCupC
  },
  {
    id: 3,
    title: "农作物种植策略优化",
    source: "2024高教杯C题",
    description: "基于土地和气候条件，建立优化模型以最大化农作物产量和收益。",
    tags: ["优化模型", "农业策略"],
    image: mcmCupC
  }
]

const filteredMMBenchExamples = computed(() => {
  if (!searchQuery.value) return mmbenchExamples.value
  const query = searchQuery.value.toLowerCase()
  return mmbenchExamples.value.filter(ex => 
    ex.title.toLowerCase().includes(query) || 
    ex.description.toLowerCase().includes(query) ||
    ex.source.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  try {
    const res = await getExamplesList()
    if (res.data && res.data.mmbench) {
      mmbenchExamples.value = res.data.mmbench.map((item: any) => ({
        ...item,
        icon: Database, // Default icon
        datasetInfo: "Standard Dataset"
      }))
    }
  } catch (error) {
    console.error("Failed to load examples list:", error)
  }
})

const selectExample = async (example: ModelingExample) => {
  try {
    isLoading.value = true
    const res = await exampleAPI(example.id.toString(), example.source)
    const task_id = res?.data?.task_id
    if (task_id) {
      router.push(`/task/${task_id}`)
    }
  } catch (error) {
    console.error("Failed to load example:", error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="mt-8 mb-12">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold tracking-tight">样例解析</h2>
        <p class="text-sm text-muted-foreground mt-1">
          精选历年数模竞赛优秀案例与 MMBench 标准数据集
        </p>
      </div>
    </div>

    <Tabs defaultValue="classic" class="w-full">
      <TabsList class="mb-6">
        <TabsTrigger value="classic">经典案例</TabsTrigger>
        <TabsTrigger value="mmbench">MMBench 数据集</TabsTrigger>
      </TabsList>

      <TabsContent value="classic">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card v-for="example in classicExamples" :key="example.id" 
            class="overflow-hidden hover:shadow-lg transition-all duration-300 border-muted group cursor-pointer"
            @click="selectExample(example)"
          >
            <div class="relative h-48 overflow-hidden bg-muted">
              <img :src="example.image" :alt="example.title" 
                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
              <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Button variant="secondary" size="sm">开始建模</Button>
              </div>
            </div>
            <CardHeader class="p-4 pb-2">
              <div class="flex justify-between items-start gap-2">
                <CardTitle class="text-base font-bold line-clamp-1">{{ example.title }}</CardTitle>
              </div>
              <CardDescription class="text-xs">{{ example.source }}</CardDescription>
            </CardHeader>
            <CardContent class="p-4 pt-0">
              <p class="text-sm text-muted-foreground line-clamp-2 mb-3 h-10">
                {{ example.description }}
              </p>
              <div class="flex flex-wrap gap-1.5">
                <Badge v-for="tag in example.tags" :key="tag" variant="secondary" class="text-xs font-normal">
                  {{ tag }}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      <TabsContent value="mmbench">
        <div class="mb-6 relative">
          <Search class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input 
            v-model="searchQuery" 
            placeholder="搜索 MMBench 数据集..." 
            class="pl-9 w-full max-w-md"
          />
        </div>
        
        <div v-if="filteredMMBenchExamples.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          <Card v-for="example in filteredMMBenchExamples" :key="example.id" 
            class="hover:border-primary/50 transition-colors group cursor-pointer"
            @click="selectExample(example)"
          >
            <CardHeader class="flex flex-row items-start gap-4 space-y-0 pb-2">
              <div class="p-2 bg-primary/10 rounded-lg text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <component :is="example.icon" class="w-6 h-6" />
              </div>
              <div class="flex-1">
                <CardTitle class="text-base font-bold">{{ example.title }}</CardTitle>
                <CardDescription class="text-xs mt-1 font-mono">{{ example.source }}</CardDescription>
              </div>
            </CardHeader>
            <CardContent class="pb-2">
              <p class="text-sm text-muted-foreground mb-4 line-clamp-2">
                {{ example.description }}
              </p>
              <div class="flex items-center gap-2 text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                <Database class="w-3 h-3" />
                <span class="font-medium">Data:</span> {{ example.datasetInfo }}
              </div>
            </CardContent>
            <CardFooter class="pt-2">
              <div class="flex flex-wrap gap-1.5">
                <Badge v-for="tag in example.tags" :key="tag" variant="outline" class="text-xs">
                  {{ tag }}
                </Badge>
              </div>
            </CardFooter>
          </Card>
        </div>
        <div v-else class="text-center py-12 text-muted-foreground">
          未找到匹配的数据集
        </div>
      </TabsContent>
    </Tabs>
  </div>
</template>
