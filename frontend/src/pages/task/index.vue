<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Separator } from '@/components/ui/separator'
import CoderEditor from '@/components/AgentEditor/CoderEditor.vue'
import WriterEditor from '@/components/AgentEditor/WriterEditor.vue'
import ModelerEditor from '@/components/AgentEditor/ModelerEditor.vue'
import ChatArea from '@/components/ChatArea.vue'
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useTaskStore } from '@/stores/task'
import { getWriterSeque } from '@/apis/commonApi';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast/use-toast'
import FilesSheet from '@/pages/task/components/FileSheet.vue'
import { evaluateTask } from '@/apis/submitModelingApi';
import { 
  ClipboardCheck, 
  Clock, 
  LayoutDashboard, 
  Brain, 
  Code2, 
  PenTool, 
  Download,
  MessageSquare
} from 'lucide-vue-next';

const { toast } = useToast()

const props = defineProps<{ task_id: string }>()
const taskStore = useTaskStore()

const writerSequence = ref<string[]>([]);

// 项目运行时长相关
const startTime = ref<number>(Date.now())
const currentTime = ref<number>(Date.now())
let timer: ReturnType<typeof setInterval> | null = null

// 格式化运行时长
const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  } else {
    return `${remainingSeconds}s`
  }
}

// 计算运行时长
const runningDuration = ref<string>('0s')
const updateDuration = () => {
  currentTime.value = Date.now()
  runningDuration.value = formatDuration(currentTime.value - startTime.value)
}

console.log('Task ID:', props.task_id)

onMounted(async () => {
  taskStore.connectWebSocket(props.task_id)
  const res = await getWriterSeque();
  writerSequence.value = Array.isArray(res.data) ? res.data : [];

  // 开始计时
  timer = setInterval(updateDuration, 1000)
  updateDuration() // 立即更新一次
})

const handleEvaluate = async () => {
  try {
    await evaluateTask(props.task_id);
    toast({
      title: '评估已触发',
      description: '正在后台进行 MMBench 评估，请留意消息通知。',
    });
  } catch (error) {
    console.error('评估触发失败:', error);
    toast({
      title: '评估触发失败',
      description: '无法启动评估，请稍后重试。',
      variant: 'destructive',
    });
  }
};


onBeforeUnmount(() => {
  taskStore.closeWebSocket()
  // 清理计时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

</script>

<template>
  <div class="fixed inset-0 flex flex-col bg-background text-foreground overflow-hidden font-sans">
    
    <!-- Top Header / Status Bar -->
    <header class="h-12 border-b flex items-center justify-between px-4 bg-card/50 backdrop-blur-sm z-10 shrink-0">
      <div class="flex items-center gap-4">
        <div class="font-bold text-lg tracking-tight flex items-center gap-2 text-primary">
           <LayoutDashboard class="w-5 h-5" />
           Fast-MM
        </div>
        <Separator orientation="vertical" class="h-4 bg-border/60" />
        <div class="flex items-center gap-2 text-xs font-mono text-muted-foreground">
          <span class="px-1.5 py-0.5 rounded bg-muted/50 border border-border/50">TASK-{{ task_id }}</span>
          <span class="flex items-center gap-1 text-indigo-500">
            <Clock class="w-3 h-3" />
            {{ runningDuration }}
          </span>
        </div>
      </div>

      <div class="flex items-center gap-2">
         <TooltipProvider>
            <Tooltip>
               <TooltipTrigger as-child>
                  <Button variant="ghost" size="icon" @click="taskStore.downloadMessages" class="h-8 w-8 text-muted-foreground hover:text-foreground">
                     <Download class="w-4 h-4" />
                  </Button>
               </TooltipTrigger>
               <TooltipContent>Download Chat Logs</TooltipContent>
            </Tooltip>
         </TooltipProvider>

         <Separator orientation="vertical" class="h-4 bg-border/60" />

         <Button variant="outline" size="sm" @click="handleEvaluate" class="h-8 gap-2 border-indigo-200 text-indigo-700 hover:bg-indigo-50 hover:text-indigo-800 dark:border-indigo-900 dark:text-indigo-400 dark:hover:bg-indigo-950">
            <ClipboardCheck class="w-3.5 h-3.5" />
            Evaluate
         </Button>
         
         <FilesSheet />
      </div>
    </header>

    <!-- Main Workspace -->
    <div class="flex-1 flex overflow-hidden">
      <ResizablePanelGroup direction="horizontal" class="h-full">
        
        <!-- Left Panel: Chat -->
        <ResizablePanel :default-size="30" :min-size="20" :max-size="50" class="border-r bg-muted/5 flex flex-col min-w-[300px]">
           <div class="h-9 border-b px-3 flex items-center text-xs font-medium text-muted-foreground bg-muted/10 uppercase tracking-wider">
              <MessageSquare class="w-3.5 h-3.5 mr-2" />
              Conversation
           </div>
           <div class="flex-1 overflow-hidden">
              <ChatArea :messages="taskStore.chatMessages" />
           </div>
        </ResizablePanel>
        
        <ResizableHandle with-handle class="bg-border/40 hover:bg-primary/50 transition-colors w-1" />

        <!-- Right Panel: Editors -->
        <ResizablePanel :default-size="70" class="bg-background flex flex-col min-w-[400px]">
           <Tabs default-value="modeler" class="h-full flex flex-col w-full">
              <div class="border-b bg-muted/5 px-2">
                 <TabsList class="h-10 bg-transparent p-0 w-full justify-start gap-1">
                    <TabsTrigger value="modeler" 
                       class="h-9 rounded-none border-b-2 border-transparent px-4 data-[state=active]:border-indigo-500 data-[state=active]:bg-background data-[state=active]:text-indigo-600 data-[state=active]:shadow-none transition-all">
                       <Brain class="w-4 h-4 mr-2" /> 
                       Modeler
                    </TabsTrigger>
                    <TabsTrigger value="coder" 
                       class="h-9 rounded-none border-b-2 border-transparent px-4 data-[state=active]:border-indigo-500 data-[state=active]:bg-background data-[state=active]:text-indigo-600 data-[state=active]:shadow-none transition-all">
                       <Code2 class="w-4 h-4 mr-2" /> 
                       Coder
                    </TabsTrigger>
                    <TabsTrigger value="writer" 
                       class="h-9 rounded-none border-b-2 border-transparent px-4 data-[state=active]:border-indigo-500 data-[state=active]:bg-background data-[state=active]:text-indigo-600 data-[state=active]:shadow-none transition-all">
                       <PenTool class="w-4 h-4 mr-2" /> 
                       Writer
                    </TabsTrigger>
                 </TabsList>
              </div>
              
              <div class="flex-1 overflow-hidden relative bg-card">
                 <TabsContent value="modeler" class="absolute inset-0 m-0 p-0 border-none data-[state=inactive]:hidden h-full w-full">
                    <ModelerEditor />
                 </TabsContent>

                 <TabsContent value="coder" class="absolute inset-0 m-0 p-0 border-none data-[state=inactive]:hidden h-full w-full">
                    <CoderEditor />
                 </TabsContent>

                 <TabsContent value="writer" class="absolute inset-0 m-0 p-0 border-none data-[state=inactive]:hidden h-full w-full">
                    <WriterEditor :messages="taskStore.writerMessages" :writerSequence="writerSequence" />
                 </TabsContent>
              </div>
           </Tabs>
        </ResizablePanel>

      </ResizablePanelGroup>
    </div>
    
    <!-- Bottom Status Bar -->
    <footer class="h-6 border-t bg-muted/20 text-[10px] flex items-center px-4 text-muted-foreground justify-between select-none">
       <div class="flex items-center gap-3">
          <span class="flex items-center gap-1"><div class="w-1.5 h-1.5 rounded-full bg-green-500"></div> System Ready</span>
          <span>Fast-MM v2.0.0</span>
       </div>
       <div class="flex items-center gap-3">
          <span>UTF-8</span>
          <span>Ln 1, Col 1</span>
       </div>
    </footer>
  </div>
</template>

<style scoped>
/* Optional: specific overrides if Tailwind is not enough */
</style>
