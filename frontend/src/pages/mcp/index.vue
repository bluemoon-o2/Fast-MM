<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import AppSidebar from '@/components/AppSidebar.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/toast/use-toast'
import { getMCPServers, addMCPServer, removeMCPServer, syncMCPTools, type MCPServerStatus } from '@/apis/mcpApi'
import { Loader2, Plus, RefreshCw, Trash2, Server } from 'lucide-vue-next'

const servers = ref<MCPServerStatus[]>([])
const loading = ref(false)
const syncing = ref(false)
const { toast } = useToast()

const isAddDialogOpen = ref(false)
const newServer = ref({
  name: '',
  type: 'stdio',
  command: '',
  args: '',
  url: '',
  enabled: true
})

const fetchServers = async () => {
  loading.value = true
  try {
    const res = await getMCPServers()
    servers.value = res.data
  } catch (error) {
    toast({
      title: "Error fetching servers",
      description: String(error),
      variant: "destructive"
    })
  } finally {
    loading.value = false
  }
}

const handleAddServer = async () => {
  try {
    const payload = {
      name: newServer.value.name,
      type: newServer.value.type as "stdio" | "sse",
      enabled: newServer.value.enabled,
      command: newServer.value.type === 'stdio' ? newServer.value.command : undefined,
      args: newServer.value.type === 'stdio' && newServer.value.args ? newServer.value.args.split(' ') : [],
      url: newServer.value.type === 'sse' ? newServer.value.url : undefined
    }
    
    await addMCPServer(payload)
    toast({ title: "Server added successfully" })
    isAddDialogOpen.value = false
    fetchServers()
    
    // Reset form
    newServer.value = {
      name: '',
      type: 'stdio',
      command: '',
      args: '',
      url: '',
      enabled: true
    }
  } catch (error) {
    toast({
      title: "Error adding server",
      description: String(error),
      variant: "destructive"
    })
  }
}

const handleRemoveServer = async (name: string) => {
  if (!confirm(`Are you sure you want to remove ${name}?`)) return
  try {
    await removeMCPServer(name)
    toast({ title: "Server removed" })
    fetchServers()
  } catch (error) {
    toast({
      title: "Error removing server",
      description: String(error),
      variant: "destructive"
    })
  }
}

const handleSync = async () => {
  syncing.value = true
  try {
    await syncMCPTools()
    toast({ title: "Tools synced successfully" })
    fetchServers()
  } catch (error) {
    toast({
      title: "Error syncing tools",
      description: String(error),
      variant: "destructive"
    })
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchServers()
})
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-16 shrink-0 items-center gap-2 px-4 border-b">
        <SidebarTrigger class="-ml-1" />
        <div class="flex items-center gap-2 font-semibold">
          <Server class="w-5 h-5" />
          MCP Servers
        </div>
      </header>

      <div class="p-6 space-y-6 max-w-5xl mx-auto w-full">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold tracking-tight">MCP Servers</h2>
            <p class="text-muted-foreground">Manage your Model Context Protocol servers and tools.</p>
          </div>
          <div class="flex gap-2">
            <Button variant="outline" @click="handleSync" :disabled="syncing">
              <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': syncing }" />
              Sync Tools
            </Button>
            
            <Dialog v-model:open="isAddDialogOpen">
              <DialogTrigger as-child>
                <Button>
                  <Plus class="w-4 h-4 mr-2" />
                  Add Server
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add MCP Server</DialogTitle>
                  <DialogDescription>
                    Connect to a local (stdio) or remote (SSE) MCP server.
                  </DialogDescription>
                </DialogHeader>
                
                <div class="grid gap-4 py-4">
                  <div class="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" v-model="newServer.name" placeholder="my-server" />
                  </div>
                  
                  <div class="grid gap-2">
                    <Label htmlFor="type">Type</Label>
                    <Select v-model="newServer.type">
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="stdio">Stdio (Local)</SelectItem>
                        <SelectItem value="sse">SSE (Remote)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <template v-if="newServer.type === 'stdio'">
                    <div class="grid gap-2">
                      <Label htmlFor="command">Command</Label>
                      <Input id="command" v-model="newServer.command" placeholder="npx, python, etc." />
                    </div>
                    <div class="grid gap-2">
                      <Label htmlFor="args">Arguments</Label>
                      <Input id="args" v-model="newServer.args" placeholder="-y @modelcontextprotocol/server-filesystem ..." />
                    </div>
                  </template>
                  
                  <template v-if="newServer.type === 'sse'">
                    <div class="grid gap-2">
                      <Label htmlFor="url">URL</Label>
                      <Input id="url" v-model="newServer.url" placeholder="http://localhost:8000/sse" />
                    </div>
                  </template>
                </div>
                
                <DialogFooter>
                  <Button @click="handleAddServer">Add Server</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div class="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Config</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Tools</TableHead>
                <TableHead class="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="loading">
                <TableCell colspan="6" class="text-center py-10">
                  <Loader2 class="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
                </TableCell>
              </TableRow>
              <TableRow v-else-if="servers.length === 0">
                <TableCell colspan="6" class="text-center py-10 text-muted-foreground">
                  No MCP servers configured. Add one to get started.
                </TableCell>
              </TableRow>
              <TableRow v-for="server in servers" :key="server.name">
                <TableCell class="font-medium">{{ server.name }}</TableCell>
                <TableCell>
                  <Badge variant="outline">{{ server.config.type }}</Badge>
                </TableCell>
                <TableCell class="font-mono text-xs text-muted-foreground max-w-[300px] truncate">
                  <span v-if="server.config.type === 'stdio'">
                    {{ server.config.command }} {{ server.config.args?.join(' ') }}
                  </span>
                  <span v-else>
                    {{ server.config.url }}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge :variant="server.status === 'connected' ? 'default' : 'destructive'">
                    {{ server.status }}
                  </Badge>
                </TableCell>
                <TableCell>{{ server.tools }}</TableCell>
                <TableCell class="text-right">
                  <Button variant="ghost" size="icon" @click="handleRemoveServer(server.name)">
                    <Trash2 class="w-4 h-4 text-destructive" />
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
