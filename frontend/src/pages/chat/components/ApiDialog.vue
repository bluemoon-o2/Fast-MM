<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useApiKeyStore } from '@/stores/apiKeys'
import { CheckCircle, XCircle, AlertCircle, Save, RotateCw } from 'lucide-vue-next'
import { validateApiKey, saveApiConfig } from '@/apis/apiKeyApi'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'

const apiKeyStore = useApiKeyStore()

// Provider definitions
const PROVIDERS = [
  { value: 'openai', label: 'OpenAI', defaultBaseUrl: 'https://api.openai.com/v1', defaultModels: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
  { value: 'anthropic', label: 'Anthropic', defaultBaseUrl: 'https://api.anthropic.com/v1', defaultModels: ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229'] },
  { value: 'dashscope', label: '通义千问', defaultBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModels: ['qwen-plus', 'qwen-turbo', 'qwen-max', 'qwen-long'] },
  { value: 'deepseek', label: 'DeepSeek', defaultBaseUrl: 'https://api.deepseek.com', defaultModels: ['deepseek-chat', 'deepseek-coder'] },
  { value: 'siliconflow', label: '硅基流动', defaultBaseUrl: 'https://api.siliconflow.cn/v1', defaultModels: ['Qwen/Qwen2.5-72B-Instruct', 'Qwen/Qwen2.5-7B-Instruct', 'deepseek-ai/DeepSeek-V3'] },
  { value: 'ollama', label: 'Ollama', defaultBaseUrl: 'http://localhost:11434/v1', defaultModels: ['llama3', 'qwen2.5:7b', 'mistral'] },
  { value: 'custom', label: '自定义', defaultBaseUrl: '', defaultModels: [] },
]

// 本地表单数据
const form = ref<{
  coordinator: { apiKey: string; baseUrl: string; modelId: string; provider: string };
  modeler: { apiKey: string; baseUrl: string; modelId: string; provider: string };
  coder: { apiKey: string; baseUrl: string; modelId: string; provider: string };
  writer: { apiKey: string; baseUrl: string; modelId: string; provider: string };
  openalex_email: string;
}>({
  coordinator: { apiKey: '', baseUrl: '', modelId: '', provider: 'openai' },
  modeler: { apiKey: '', baseUrl: '', modelId: '', provider: 'openai' },
  coder: { apiKey: '', baseUrl: '', modelId: '', provider: 'openai' },
  writer: { apiKey: '', baseUrl: '', modelId: '', provider: 'openai' },
  openalex_email: ''
})

// 验证状态
const validating = ref(false)
const validationResults = ref({
  coordinator: { valid: false, message: '' },
  modeler: { valid: false, message: '' },
  coder: { valid: false, message: '' },
  writer: { valid: false, message: '' },
  openalex_email: { valid: false, message: '' }
})

// 计算所有验证是否都通过
const allValid = computed(() => {
  // Check if at least one config is filled and valid, or allow skip if user wants?
  // For now, strict validation on what's entered.
  return true // We allow saving even if not fully validated, but maybe warn?
})

// 模型配置列表
const modelConfigs = computed(() => [
  { key: 'coordinator', label: 'Coordinator Agent (协调者)', description: '负责任务拆解与流程调度' },
  { key: 'modeler', label: 'Modeler Agent (建模手)', description: '负责数学建模与公式推导' },
  { key: 'coder', label: 'Coder Agent (代码手)', description: '负责代码编写与运行调试' },
  { key: 'writer', label: 'Writer Agent (论文手)', description: '负责论文撰写与图表整合' }
])

// 从 store 加载数据到表单
const loadFromStore = () => {
  // 使用 Object.assign 保持响应式对象的引用，避免替换整个对象
  Object.assign(form.value.coordinator, {
    ...apiKeyStore.coordinatorConfig,
    provider: apiKeyStore.coordinatorConfig.provider || 'openai'
  })
  Object.assign(form.value.modeler, {
    ...apiKeyStore.modelerConfig,
    provider: apiKeyStore.modelerConfig.provider || 'openai'
  })
  Object.assign(form.value.coder, {
    ...apiKeyStore.coderConfig,
    provider: apiKeyStore.coderConfig.provider || 'openai'
  })
  Object.assign(form.value.writer, {
    ...apiKeyStore.writerConfig,
    provider: apiKeyStore.writerConfig.provider || 'openai'
  })
  form.value.openalex_email = apiKeyStore.openalexEmail
}

// Handle Provider Change
const handleProviderChange = (agentKey: keyof typeof form.value, newProvider: string) => {
  const providerConfig = PROVIDERS.find(p => p.value === newProvider)
  if (providerConfig && agentKey !== 'openalex_email') {
    // Auto-fill Base URL if the new provider has a default one
    if (providerConfig.defaultBaseUrl) {
       form.value[agentKey].baseUrl = providerConfig.defaultBaseUrl
    }
    
    // Auto-select first model if the new provider has default models
    if (providerConfig.defaultModels.length > 0) {
      form.value[agentKey].modelId = providerConfig.defaultModels[0]
    }
  }
}

// 保存表单数据到 store
const saveToStore = async () => {
  // 先保存到前端 store
  apiKeyStore.setCoordinatorConfig(form.value.coordinator)
  apiKeyStore.setModelerConfig(form.value.modeler)
  apiKeyStore.setCoderConfig(form.value.coder)
  apiKeyStore.setWriterConfig(form.value.writer)
  apiKeyStore.setOpenalexEmail(form.value.openalex_email)
  
  try {
    await saveApiConfig({
      coordinator: form.value.coordinator,
      modeler: form.value.modeler,
      coder: form.value.coder,
      writer: form.value.writer,
      openalex_email: form.value.openalex_email
    })
    // toast success?
  } catch (error) {
    console.error('保存配置到后端失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadFromStore()
})

// 定义 emits
const emit = defineEmits<{ (e: 'update:open', value: boolean): void }>()

// 定义 props
const props = defineProps<{ open: boolean }>()

// 更新 open 状态
const updateOpen = (value: boolean) => {
  emit('update:open', value)
}

// 保存并关闭
const saveAndClose = async () => {
  await saveToStore()
  updateOpen(false)
}

// 验证大模型 API Key
const validateModelApiKey = async (config: { apiKey: string, baseUrl: string, modelId: string, provider: string }) => {
  // Skip validation for Ollama if no API key is needed (usually) but we check connectivity
  if (config.provider !== 'ollama' && !config.apiKey) {
    return { valid: false, message: 'API Key is required' }
  }

  if (!config.modelId) {
    return { valid: false, message: 'Model ID is required' }
  }

  try {
    const result = await validateApiKey({
      api_key: config.apiKey || 'ollama', // Pass dummy for ollama
      base_url: config.baseUrl,
      model_id: config.modelId,
      provider: config.provider // Add provider
    })

    return {
      valid: result.data.valid,
      message: result.data.message
    }
  } catch (error) {
    return {
      valid: false,
      message: 'Connection failed'
    }
  }
}

// 一键验证所有 API Keys
const validateAllApiKeys = async () => {
  validating.value = true

  validationResults.value = {
    coordinator: { valid: false, message: '' },
    modeler: { valid: false, message: '' },
    coder: { valid: false, message: '' },
    writer: { valid: false, message: '' },
    openalex_email: { valid: false, message: '' }
  }

  try {
    for (const config of modelConfigs.value) {
      const key = config.key as keyof typeof validationResults.value
      const formKey = config.key as keyof typeof form.value

      validationResults.value[key] = { valid: false, message: 'Checking...' }
      validationResults.value[key] = await validateModelApiKey(form.value[formKey] as any)
      
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  } finally {
    validating.value = false
  }
}

</script>

<template>
  <Dialog :open="open" @update:open="updateOpen">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto sm:max-w-[900px]">
      <DialogHeader>
        <DialogTitle class="text-xl font-bold flex items-center gap-2">
          <Save class="w-5 h-5 text-primary" />
          模型配置 (Model Configuration)
        </DialogTitle>
        <DialogDescription>
           为每个 Agent 配置合适的大模型提供商 (LLM Provider)。
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        
        <!-- Agents Configuration Grid -->
        <div class="grid grid-cols-1 gap-6">
          <div v-for="config in modelConfigs" :key="config.key" 
               class="rounded-lg border bg-card text-card-foreground shadow-sm p-4 space-y-3">
            
            <div class="flex items-center justify-between">
               <div class="flex items-center gap-2">
                  <Badge variant="outline" class="font-mono">{{ config.key.toUpperCase() }}</Badge>
                  <span class="text-sm font-medium text-muted-foreground">{{ config.description }}</span>
               </div>
               
               <!-- Validation Status -->
               <div v-if="validationResults[config.key as keyof typeof validationResults].message" class="flex items-center gap-1.5 text-xs">
                  <component :is="validationResults[config.key as keyof typeof validationResults].valid ? CheckCircle : (validationResults[config.key as keyof typeof validationResults].message === 'Checking...' ? RotateCw : XCircle)"
                             :class="[
                               'w-4 h-4', 
                               validationResults[config.key as keyof typeof validationResults].valid ? 'text-green-500' : 
                               (validationResults[config.key as keyof typeof validationResults].message === 'Checking...' ? 'text-blue-500 animate-spin' : 'text-red-500')
                             ]" />
                  <span :class="validationResults[config.key as keyof typeof validationResults].valid ? 'text-green-600' : 'text-red-600'">
                     {{ validationResults[config.key as keyof typeof validationResults].message }}
                  </span>
               </div>
            </div>

            <div class="grid grid-cols-12 gap-3 items-end">
              
              <!-- Provider Selection -->
              <div class="col-span-3">
                <Label class="text-xs mb-1.5 block text-muted-foreground">提供商 (Provider)</Label>
                <Select v-model="(form[config.key as keyof typeof form] as any).provider" 
                        @update:modelValue="(val) => handleProviderChange(config.key as any, val)">
                  <SelectTrigger class="h-8 text-xs">
                    <SelectValue placeholder="选择提供商" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="p in PROVIDERS" :key="p.value" :value="p.value">
                      {{ p.label }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- Base URL -->
              <div class="col-span-4">
                 <Label class="text-xs mb-1.5 block text-muted-foreground">API 域名 (Base URL)</Label>
                 <Input v-model="(form[config.key as keyof typeof form] as any).baseUrl" class="h-8 text-xs font-mono" placeholder="https://..." />
              </div>

              <!-- Model ID -->
              <div class="col-span-3">
                 <Label class="text-xs mb-1.5 block text-muted-foreground">模型名称 (Model ID)</Label>
                 <div class="relative">
                   <Input v-model="(form[config.key as keyof typeof form] as any).modelId" class="h-8 text-xs font-mono" placeholder="gpt-4o" list="model-suggestions" />
                 </div>
              </div>

              <!-- API Key -->
              <div class="col-span-2">
                 <Label class="text-xs mb-1.5 block text-muted-foreground">API 密钥 (API Key)</Label>
                 <Input v-model="(form[config.key as keyof typeof form] as any).apiKey" 
                        type="password" 
                        class="h-8 text-xs font-mono" 
                        :placeholder="(form[config.key as keyof typeof form] as any).provider === 'ollama' ? '无需填写' : 'sk-...'" 
                        :disabled="(form[config.key as keyof typeof form] as any).provider === 'ollama'"
                 />
              </div>

            </div>
          </div>
        </div>

        <Separator />

        <!-- OpenAlex Config -->
        <div class="rounded-lg border bg-muted/20 p-4 flex items-center gap-4">
           <div class="flex-1">
              <Label class="text-sm font-semibold">OpenAlex 邮箱 (OpenAlex Email)</Label>
              <p class="text-xs text-muted-foreground mt-1">用于访问学术论文数据的必需字段。</p>
           </div>
           <Input v-model="form.openalex_email" class="w-64 h-9" placeholder="email@example.com" />
        </div>

      </div>

      <DialogFooter class="flex items-center justify-between sm:justify-between w-full">
        <Button variant="outline" @click="validateAllApiKeys" :disabled="validating">
          <RotateCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': validating }" />
          验证连接 (Verify)
        </Button>
        <div class="flex gap-2">
          <Button variant="ghost" @click="updateOpen(false)">取消 (Cancel)</Button>
          <Button @click="saveAndClose">保存配置 (Save)</Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
