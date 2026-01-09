<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
    <!-- Navbar -->
    <nav class="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto">
      <div class="flex items-center gap-2">
        <img src="@/assets/icon.png" alt="logo" class="w-8 h-8 opacity-90" />
        <span class="text-xl font-bold tracking-tight">Fast-MM</span>
      </div>
      <div class="flex items-center gap-4">
        <a :href="GITHUB_LINK" target="_blank" class="text-slate-500 hover:text-slate-900 transition-colors">
          <Github class="w-5 h-5" />
        </a>
      </div>
    </nav>

    <!-- Hero Section -->
    <main class="flex-grow flex flex-col justify-center items-center text-center px-4 py-20">
      <div class="max-w-4xl mx-auto space-y-8">
        <div class="space-y-4">
          <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900">
            Mathematical Modeling <br />
            <span class="text-indigo-600">Redefined.</span>
          </h1>
          <p class="text-xl md:text-2xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            The next-generation autonomous agent for mathematical modeling, coding, and paper writing.
            Fast, Accurate, and Elegant.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 justify-center pt-8">
          <button @click="router.push('/chat')" class="px-8 py-4 bg-indigo-600 text-white rounded-full font-semibold text-lg hover:bg-indigo-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1">
            Get Started
          </button>
          <a :href="GITHUB_LINK" target="_blank" class="px-8 py-4 bg-white text-slate-900 border border-slate-200 rounded-full font-semibold text-lg hover:bg-slate-50 transition-all shadow-sm hover:shadow-md">
            View on GitHub
          </a>
        </div>
      </div>

      <!-- Feature Grid (Minimal) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-24 px-4">
        <div class="p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-100">
          <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4 mx-auto">
            <Zap class="w-6 h-6 text-indigo-600" />
          </div>
          <h3 class="text-xl font-bold mb-2">Lightning Fast</h3>
          <p class="text-slate-600">Accelerate your modeling process from days to minutes with autonomous workflows.</p>
        </div>
        <div class="p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-100">
          <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4 mx-auto">
            <Brain class="w-6 h-6 text-indigo-600" />
          </div>
          <h3 class="text-xl font-bold mb-2">Intelligent Core</h3>
          <p class="text-slate-600">Powered by advanced DAG orchestration and Actor-Critic iteration mechanisms.</p>
        </div>
        <div class="p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-100">
          <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4 mx-auto">
            <FileText class="w-6 h-6 text-indigo-600" />
          </div>
          <h3 class="text-xl font-bold mb-2">Publication Ready</h3>
          <p class="text-slate-600">Generates complete, formatted papers ready for submission and review.</p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-8 text-center text-slate-400 text-sm">
      <p>© {{ new Date().getFullYear() }} Fast-MM. Open Source under Apache 2.0.</p>
    </footer>
  </div>
</template>

<script setup>
import { Github, Zap, Brain, FileText } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { GITHUB_LINK } from '@/utils/const'

const router = useRouter()
</script>

<style scoped>
/* Add any specific transitions or custom font adjustments here if needed */
</style>
