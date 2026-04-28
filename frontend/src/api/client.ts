const apiBase = import.meta.env.VITE_API_BASE_URL ?? ''

function apiUrl(path: string): string {
  if (path.startsWith('http')) return path
  const p = path.startsWith('/') ? path : `/${path}`
  return `${apiBase}${p}`
}

export type ChatHistoryItem = { message: string; is_bot: boolean }

export async function saveUsername(username: string): Promise<{
  success: boolean
  chat_history: ChatHistoryItem[]
}> {
  const res = await fetch(apiUrl('/api/session/username'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ username }),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function sendChatMessage(
  username: string,
  message: string,
): Promise<{ response: string }> {
  const res = await fetch(apiUrl('/api/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ username, message }),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed (${res.status})`)
  }
  return res.json()
}

export type ResumeAnalyzeEvent = {
  progress?: number
  message?: string
  final_score?: number
  skill_score?: number
  experience_score?: number
  matched_skills?: string[]
  missing_skills?: string[]
}

export async function analyzeResumeStream(
  file: File,
  jobDescription: string,
  onEvent: (data: ResumeAnalyzeEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const form = new FormData()
  form.append('file', file)
  form.append('job_description', jobDescription)

  const res = await fetch(apiUrl('/api/resume/analyze'), {
    method: 'POST',
    body: form,
    signal,
  })

  if (!res.ok || !res.body) {
    throw new Error(`Analyze failed (${res.status})`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  const feed = (chunk: Uint8Array) => {
    buf += decoder.decode(chunk, { stream: true })
    const parts = buf.split('\n\n')
    buf = parts.pop() ?? ''
    for (const part of parts) {
      for (const line of part.split(/\r?\n/)) {
        if (line.startsWith('data:')) {
          try {
            onEvent(JSON.parse(line.slice(5).trim()) as ResumeAnalyzeEvent)
          } catch {
            /* ignore */
          }
        }
      }
    }
  }

  try {
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      if (value) feed(value)
    }
    if (buf) {
      for (const line of buf.split(/\r?\n/)) {
        if (line.startsWith('data:')) {
          try {
            onEvent(JSON.parse(line.slice(5).trim()) as ResumeAnalyzeEvent)
          } catch {
            /* ignore */
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
