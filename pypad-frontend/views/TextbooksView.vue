<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { textbookApi } from '@/services/api'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()

const markdownContent = ref('')
const bookTitle = ref('')
const uploading = ref(false)
const uploadResult = ref<{ success: boolean; message: string } | null>(null)
const dragOver = ref(false)

const handleFileUpload = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  readFile(file)
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) readFile(file)
}

const readFile = (file: File) => {
  if (!file.name.endsWith('.md') && !file.name.endsWith('.markdown')) {
    uploadResult.value = { success: false, message: '仅支持 Markdown (.md) 文件' }
    return
  }
  if (!bookTitle.value) {
    bookTitle.value = file.name.replace(/\.md$/, '')
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    markdownContent.value = e.target?.result as string || ''
  }
  reader.readAsText(file)
}

const uploadTextbook = async () => {
  if (!markdownContent.value.trim()) {
    uploadResult.value = { success: false, message: '请先选择或粘贴 Markdown 内容' }
    return
  }

  uploading.value = true
  uploadResult.value = null

  try {
    const token = localStorage.getItem('auth_token')
    const res = await fetch('http://localhost:8000/api/textbook/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        content: markdownContent.value,
        bookTitle: bookTitle.value || '自定义教材',
      }),
    })
    const data = await res.json()
    uploadResult.value = {
      success: data.success,
      message: data.message || (data.success ? '上传成功' : '上传失败'),
    }
    if (data.success) {
      await knowledgeStore.loadData()
    }
  } catch (err) {
    uploadResult.value = { success: false, message: '上传失败，请检查后端服务' }
  } finally {
    uploading.value = false
  }
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="textbooks-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>教材管理</h1>
      </div>
    </header>

    <div class="textbooks-content">
      <!-- Upload Section -->
      <div class="section-card glass-card">
        <h3>📤 导入 Markdown 教材</h3>
        <p class="section-desc">上传 Markdown 格式教材，系统将自动解析章节结构、提取知识点并构建知识图谱。</p>

        <!-- Book Title -->
        <div class="form-group">
          <label>教材名称</label>
          <input v-model="bookTitle" type="text" placeholder="输入教材名称（可选）" class="form-input" />
        </div>

        <!-- File Drop Zone -->
        <div
          class="drop-zone"
          :class="{ dragover: dragOver }"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop="handleDrop"
        >
          <div class="drop-icon">📁</div>
          <p>拖拽 .md 文件到此处，或</p>
          <label class="file-btn">
            选择文件
            <input type="file" accept=".md,.markdown" @change="handleFileUpload" hidden />
          </label>
        </div>

        <!-- Or Paste Content -->
        <div class="form-group">
          <label>或直接粘贴 Markdown 内容</label>
          <textarea
            v-model="markdownContent"
            placeholder="# 章节标题&#10;&#10;知识点内容...&#10;&#10;```python&#10;print('hello')&#10;```"
            rows="10"
            class="form-textarea"
          ></textarea>
        </div>

        <!-- Upload Button -->
        <button
          class="btn-primary"
          :disabled="uploading || !markdownContent.trim()"
          @click="uploadTextbook"
        >
          {{ uploading ? '解析中...' : '开始导入' }}
        </button>

        <!-- Result -->
        <div v-if="uploadResult" class="upload-result" :class="uploadResult.success ? 'success' : 'error'">
          {{ uploadResult.message }}
        </div>
      </div>

      <!-- Current Knowledge Stats -->
      <div class="section-card glass-card">
        <h3>📊 当前知识库</h3>
        <div class="kb-stats">
          <div class="kb-stat">
            <span class="kb-num">{{ knowledgeStore.nodes.filter(n => n.category !== 'Root' && n.category !== 'Domain').length }}</span>
            <span class="kb-label">知识节点</span>
          </div>
          <div class="kb-stat">
            <span class="kb-num">{{ knowledgeStore.edges.length }}</span>
            <span class="kb-label">关系边</span>
          </div>
          <div class="kb-stat">
            <span class="kb-num">{{ knowledgeStore.strongNodes.length }}</span>
            <span class="kb-label">已掌握</span>
          </div>
        </div>
      </div>

      <!-- Markdown Format Guide -->
      <div class="section-card glass-card">
        <h3>📖 Markdown 格式指南</h3>
        <div class="guide-content">
          <p>系统支持以下 Markdown 结构自动解析为知识点：</p>
          <pre class="code-block"># 一级标题 → 知识域（Domain）
## 二级标题 → 知识点（KnowledgeNode）
### 三级标题 → 子知识点

```python
# 代码块自动关联到最近的知识点
print("Hello PyPad")
```</pre>
          <ul>
            <li><code>#</code> H1 标题映射为知识域分类</li>
            <li><code>##</code> H2 标题映射为独立知识点</li>
            <li><code>###</code> H3 标题映射为子知识点</li>
            <li>代码块自动切割并关联到对应知识点</li>
            <li>知识点之间的先后顺序自动建立 <code>prerequisite</code> 关系</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.textbooks-view {
  width: 100vw; min-height: 100vh; background: var(--bg-primary); overflow-y: auto;
}

.view-header {
  position: sticky; top: 0; z-index: 20; padding: 16px 32px;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0; }

.back-btn {
  background: transparent; border: 1px solid var(--border); border-radius: 8px;
  padding: 6px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; transition: all 0.2s;
}
.back-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.textbooks-content {
  max-width: 800px; margin: 24px auto; padding: 0 24px;
  display: flex; flex-direction: column; gap: 20px;
}

.glass-card {
  background: rgba(255,255,255,0.7); border: 1px solid var(--border);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.section-card { padding: 24px; }
.section-card h3 { font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0 0 8px; }
.section-desc { font-size: 13px; color: var(--text-secondary); margin: 0 0 20px; }

.form-group { margin-bottom: 16px; }
.form-group label {
  display: block; font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;
}

.form-input {
  width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 14px; color: var(--text-primary); background: rgba(255,255,255,0.8);
  outline: none; transition: border-color 0.2s;
}
.form-input:focus { border-color: var(--accent); }

.form-textarea {
  width: 100%; padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 13px; font-family: 'JetBrains Mono', monospace; line-height: 1.6;
  color: var(--text-primary); background: rgba(255,255,255,0.8);
  outline: none; resize: vertical; transition: border-color 0.2s;
}
.form-textarea:focus { border-color: var(--accent); }

.drop-zone {
  border: 2px dashed var(--border); border-radius: 12px;
  padding: 32px; text-align: center; margin-bottom: 16px;
  transition: all 0.2s; cursor: pointer;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--accent); background: rgba(99,102,241,0.03);
}
.drop-icon { font-size: 32px; margin-bottom: 8px; }
.drop-zone p { font-size: 13px; color: var(--text-secondary); margin: 0 0 8px; }

.file-btn {
  display: inline-block; padding: 6px 14px; border-radius: 99px;
  background: var(--accent); color: #fff; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.file-btn:hover { background: var(--accent-hover); }

.btn-primary {
  padding: 10px 24px; border-radius: 99px;
  background: var(--accent); color: #fff; border: none;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-primary:hover { background: var(--accent-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.upload-result {
  margin-top: 12px; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 500;
}
.upload-result.success { background: rgba(16,185,129,0.1); color: #10b981; }
.upload-result.error { background: rgba(239,68,68,0.1); color: #ef4444; }

.kb-stats { display: flex; gap: 24px; margin-top: 8px; }
.kb-stat { display: flex; flex-direction: column; align-items: center; }
.kb-num { font-size: 24px; font-weight: 800; color: #6366f1; }
.kb-label { font-size: 12px; color: var(--text-secondary); }

.guide-content { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.guide-content p { margin: 0 0 12px; }

.code-block {
  background: #1e1e2e; color: #cdd6f4; padding: 16px; border-radius: 8px;
  font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.6;
  overflow-x: auto; margin: 0 0 12px;
}

.guide-content ul { padding-left: 20px; margin: 0; }
.guide-content li { margin-bottom: 6px; }
.guide-content code {
  background: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 3px;
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
}
</style>
