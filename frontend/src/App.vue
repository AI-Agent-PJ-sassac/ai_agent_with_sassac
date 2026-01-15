
<script setup>
import { ref, watch, nextTick } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
    html: true,
    breaks: true,
    linkify: true
})

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const fileInput = ref(null)
const uploadStatus = ref('')
const messagesContainer = ref(null)

// backend URL (via Vite proxy)
const API_URL = '/api' 

// Generate or retrieve Session ID
const getSessionId = () => {
    let sid = sessionStorage.getItem('ai_agent_session_id')
    if (!sid) {
        sid = 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now().toString(36)
        sessionStorage.setItem('ai_agent_session_id', sid)
    }
    return sid
}

const sessionId = ref(getSessionId())

// Configure Axios with Session ID
axios.interceptors.request.use(config => {
    config.headers['X-Session-ID'] = sessionId.value
    return config
}) 

// Auto-scroll to bottom
const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

watch(messages, scrollToBottom, { deep: true })

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const question = userInput.value
  messages.value.push({ role: 'user', content: question })
  userInput.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const response = await axios.post(`${API_URL}/chat`, { question })
    const result = response.data
    
    // Format references
    let refText = ''
    if (result.warnings && result.warnings.length) {
      refText += '<div class="font-semibold text-amber-600 mb-2">⚠️ 주의사항</div><ul class="list-disc pl-4 space-y-1">' + result.warnings.map(w => `<li>${w}</li>`).join('') + '</ul>'
    }
    
    // Only show search results count if relevant, or detailed list if implementing that feature later
    // const searchCount = result.search_results?.length || 0

    messages.value.push({
      role: 'assistant',
      content: result.answer,
      references: refText,
      searchResults: result.search_results || []
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '❌ 오류가 발생했습니다: ' + (error.response?.data?.detail || error.message),
      isError: true
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const hasUploadedFiles = ref(false)
const showUploadModal = ref(false)
const uploadStep = ref('idle') // idle, uploading, done, error
const uploadMessage = ref('')
const uploadedChunks = ref(0)
const uploadedFileName = ref('')

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)
  
  // 모달 표시 및 상태 초기화
  uploadedFileName.value = file.name
  uploadStep.value = 'uploading'
  uploadMessage.value = '문서를 분석하고 있습니다 (HWP/PDF/DOCX 지원)...'
  showUploadModal.value = true
  
  try {
    const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
    
    // 성공 상태 업데이트
    uploadedChunks.value = response.data.chunks
    uploadStep.value = 'done'
    uploadMessage.value = '업로드가 완료되었습니다!'
    // hasUploadedFiles.value = true // 모달 닫을 때 전환
    
    // 시스템 메시지 로그 (선택사항, 모달 닫힌 후 기록용)
    messages.value.push({
        role: 'system',
        content: `✅ **${file.name}** 업로드 완료 (${response.data.chunks} 청크)`
    })

  } catch (error) {
    // 에러 상태 업데이트
    uploadStep.value = 'error'
    uploadMessage.value = '업로드에 실패했습니다: ' + (error.response?.data?.detail || error.message)
    
     messages.value.push({
        role: 'system',
        content: `❌ **${file.name}** 업로드 실패`
    })
  }
  
  // Reset input
  if (fileInput.value) fileInput.value.value = ''
}

const closeUploadModal = () => {
    // 업로드가 성공적으로 완료된 상태에서 닫으면 채팅 화면으로 전환
    if (uploadStep.value === 'done') {
        hasUploadedFiles.value = true
    }
    showUploadModal.value = false
    uploadStep.value = 'idle'
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const isRefreshing = ref(false)
const refreshDatabase = async () => {
    if (!confirm('현재 업로드된 모든 문서를 기반으로 AI 데이터베이스를 재구축하시겠습니까?')) return

    isRefreshing.value = true
    try {
        const response = await axios.post(`${API_URL}/db/refresh`)
        messages.value.push({ 
            role: 'system', 
            content: `🔄 **DB 재구축 완료**: ${response.data.chunks}개 청크가 인덱싱되었습니다.` 
        })
        if(response.data.chunks > 0) hasUploadedFiles.value = true
    } catch (error) {
        messages.value.push({ 
            role: 'system', 
            content: `❌ **DB 재구축 실패**: ${error.response?.data?.detail || error.message}` 
        })
    } finally {
        isRefreshing.value = false
    }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-slate-50 text-slate-800 font-sans">
    
    <!-- Top Configuration / Status bar (Optional, can be used for connection status) -->
    
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg text-white font-bold text-xl">
            AI
          </div>
          <div>
            <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
              인수인계 AI 에이전트
            </h1>
            <p class="text-xs text-slate-500 font-medium">Smart Workplace Assistant</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
            <button 
                @click="refreshDatabase"
                :disabled="isRefreshing"
                class="group flex items-center gap-2 px-3 py-2 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-all duration-200"
                title="AI 데이터베이스 새로고침"
            >
                <span v-if="isRefreshing" class="animate-spin">⏳</span>
                <span v-else class="text-lg group-hover:rotate-180 transition-transform">🔄</span>
                <span class="text-sm font-medium hidden sm:inline">DB 초기화</span>
            </button>
            
          <!-- Hidden File Input -->
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileUpload" 
            class="hidden" 
            accept=".pdf,.docx,.hwp,.hwpx"
          />
          
          <button 
            @click="triggerFileInput"
            :disabled="uploadStatus === 'uploading'"
            class="group flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all duration-200 shadow-sm disabled:opacity-50"
          >
            <span v-if="uploadStatus === 'uploading'" class="animate-spin">⏳</span>
            <span v-else class="text-lg group-hover:scale-110 transition-transform">📎</span>
            <span class="text-sm font-medium text-slate-600 group-hover:text-indigo-600">문서 업로드</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Landing / Onboarding Screen -->
    <div v-if="!hasUploadedFiles" class="flex-1 flex flex-col items-center justify-center p-6 text-center animate-fade-in-up">
        <div class="mb-8 p-6 bg-indigo-50 rounded-full inline-block animate-bounce-slow">
            <span class="text-6xl">📁</span>
        </div>
        <h2 class="text-3xl font-bold text-slate-800 mb-4">인수인계 문서를 먼저 업로드해주세요!</h2>
        <p class="text-slate-500 max-w-lg mb-8 leading-relaxed">
            원활한 업무 인수인계를 위해 관련 문서(PDF, DOCX, HWP, HWPX)를<br>
            먼저 등록해주시면 AI가 내용을 분석합니다.
        </p>
        
        <button 
            @click="triggerFileInput"
            class="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-bold rounded-2xl shadow-xl shadow-indigo-200 hover:scale-105 transition-all duration-300 flex items-center gap-3"
        >
            <span>📄 문서 선택하기</span>
        </button>
        
         <div class="mt-8 grid grid-cols-2 gap-4 text-xs text-slate-400">
            <div class="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-slate-100">
                <span>✅</span> PDF / DOCX
            </div>
             <div class="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-slate-100">
                <span>✅</span> HWP / HWPX
            </div>
        </div>
    </div>

    <!-- Chat Area (Hidden until files uploaded) -->
    <main v-else class="flex-1 overflow-hidden relative">
      <div ref="messagesContainer" class="h-full overflow-y-auto px-4 py-6 scroll-smooth">
        <div class="max-w-3xl mx-auto flex flex-col gap-6 pb-24">
            
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="text-center py-20 px-4">
            <div class="inline-block p-4 rounded-full bg-indigo-50 mb-4 animate-bounce-slow">
              <span class="text-4xl">👋</span>
            </div>
            <h2 class="text-2xl font-bold text-slate-800 mb-2">문서 분석이 완료되었습니다!</h2>
            <p class="text-slate-500 max-w-md mx-auto">
              이제 궁금한 규정, 절차, 보고서 작성법 등을 물어보세요.<br>
              추가 문서는 언제든 상단 버튼으로 업로드 가능합니다.
            </p>
          </div>

          <!-- Message List -->
          <div 
            v-for="(msg, index) in messages" 
            :key="index" 
            :class="[
              'flex gap-4 w-full max-w-3xl animate-fade-in-up',
              msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            ]"
          >
            <!-- Avatar -->
            <div 
                class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm text-lg select-none"
                :class="msg.role === 'user' ? 'bg-indigo-100 text-indigo-600' : 'bg-white border border-slate-100 text-purple-600'"
            >
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>

            <!-- Bubble -->
            <div 
                class="flex flex-col gap-2 max-w-[85%]"
                :class="msg.role === 'user' ? 'items-end' : 'items-start'"
            >
                <div 
                  class="px-5 py-3.5 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap"
                  :class="[
                    msg.role === 'user' 
                      ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-tr-sm' 
                      : 'bg-white border border-slate-100 text-slate-700 rounded-tl-sm'
                  ]"
                >
                    <div v-if="msg.role === 'assistant'" class="prose prose-sm prose-indigo max-w-none" v-html="md.render(msg.content || '')"></div>
                    <div v-else>{{ msg.content }}</div>
                </div>

                <!-- References / Search Results -->
                <div v-if="msg.searchResults && msg.searchResults.length > 0" class="w-full">
                    <details class="group bg-slate-50 border border-slate-200 rounded-xl overflow-hidden transition-all duration-300">
                        <summary class="flex items-center gap-2 px-4 py-2 cursor-pointer bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider select-none">
                            <span class="group-open:rotate-90 transition-transform duration-200">▶</span>
                            <span>참조 문서 found ({{ msg.searchResults.length }})</span>
                        </summary>
                        <div class="p-3 space-y-2">
                            <div v-for="(doc, idx) in msg.searchResults" :key="idx" class="p-3 bg-white rounded-lg border border-slate-100 shadow-sm text-xs hover:shadow-md transition-shadow">
                                <div class="font-bold text-indigo-600 mb-1 flex items-center gap-1">
                                    📄 {{ doc.metadata?.source || 'Unknown Source' }}
                                </div>
                                <div class="text-slate-500 line-clamp-2">
                                    {{ doc.page_content ? doc.page_content.substring(0, 150) : '' }}...
                                </div>
                            </div>
                        </div>
                    </details>
                </div>
                
                <!-- System Alerts / Warnings -->
                <div v-if="msg.references" class="w-full bg-amber-50 border-l-4 border-amber-400 p-3 rounded-r-lg text-sm text-slate-700 shadow-sm" v-html="msg.references"></div>
            </div>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="flex gap-4 animate-pulse">
            <div class="w-10 h-10 bg-slate-200 rounded-full"></div>
            <div class="flex-1 space-y-2 py-2">
                <div class="h-2 bg-slate-200 rounded w-1/4"></div>
                <div class="h-2 bg-slate-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Input Area -->
      <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white via-white to-transparent pt-10 pb-6 px-4">
        <div class="max-w-3xl mx-auto relative shadow-2xl rounded-2xl bg-white ring-1 ring-slate-900/5">
            <input 
              v-model="userInput" 
              @keyup.enter="sendMessage" 
              placeholder="무엇을 도와드릴까요? (Enter to send)" 
              class="w-full py-4 pl-6 pr-16 bg-transparent rounded-2xl focus:outline-none text-slate-700 placeholder:text-slate-400"
              :disabled="isLoading"
            />
            <button 
              @click="sendMessage"
              :disabled="isLoading || !userInput.trim()"
              class="absolute right-2 top-2 bottom-2 aspect-square bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
              </svg>
            </button>
        </div>
        <p class="text-center text-[10px] text-slate-400 mt-3">
            AI 에이전트는 실수할 수 있습니다. 중요한 정보는 반드시 원문서를 확인하세요.
        </p>
      </div>

    </main>
    
    <!-- Upload Status Modal (Keep existing) -->
    <div v-if="showUploadModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
        <!-- ... [Modals content unchanged] ... -->
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full flex flex-col items-center gap-6 animate-fade-in-up">
            
            <!-- Uploading State -->
            <div v-if="uploadStep === 'uploading'" class="flex flex-col items-center gap-4">
                <div class="relative w-16 h-16">
                    <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                </div>
                <div class="text-center">
                    <h3 class="text-lg font-bold text-slate-800">문서 업로드 중</h3>
                    <p class="text-sm text-slate-500 mt-1">{{ uploadedFileName }}</p>
                    <p class="text-xs text-indigo-500 mt-2 font-medium animate-pulse">{{ uploadMessage }}</p>
                </div>
            </div>

            <!-- Done State -->
            <div v-else-if="uploadStep === 'done'" class="flex flex-col items-center gap-4">
                <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-3xl mb-2 animate-bounce-slow">
                    ✅
                </div>
                <div class="text-center">
                    <h3 class="text-xl font-bold text-slate-800">업로드 완료!</h3>
                    <p class="text-sm text-slate-600 mt-2">
                        총 <span class="font-bold text-indigo-600">{{ uploadedChunks }}</span>개 청크가 저장되었습니다.
                    </p>
                </div>
                <button 
                    @click="closeUploadModal"
                    class="mt-2 w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-indigo-200"
                >
                    확인 (OK)
                </button>
            </div>

            <!-- Error State -->
            <div v-else-if="uploadStep === 'error'" class="flex flex-col items-center gap-4">
                <div class="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-3xl mb-2">
                    ❌
                </div>
                <div class="text-center">
                    <h3 class="text-lg font-bold text-slate-800">업로드 실패</h3>
                    <p class="text-xs text-red-500 mt-2 bg-red-50 p-2 rounded break-all">{{ uploadMessage }}</p>
                </div>
                <button 
                    @click="closeUploadModal"
                    class="mt-2 w-full py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl transition-colors"
                >
                    닫기
                </button>
            </div>

        </div>
    </div>
  </div>
</template>>

<style>
/* Utilities specific to this component or animations */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fade-in-up 0.4s ease-out forwards;
}

.animate-bounce-slow {
    animation: bounce 2s infinite;
}

/* Scrollbar tweaks */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent; 
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1; 
  border-radius: 10px;
}
</style>
