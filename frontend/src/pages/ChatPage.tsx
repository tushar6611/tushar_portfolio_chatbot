import { useCallback, useEffect, useRef, useState } from 'react'
import { sendChatMessage, saveUsername, type ChatHistoryItem } from '../api/client'
import { LinkifyText } from '../components/LinkifyText'
import { ResumeMatchModal } from '../components/ResumeMatchModal'
import { getStoredUsername } from '../lib/session'

type Row = { id: string; text: string; isUser: boolean }

function id() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function ChatPage() {
  const [messages, setMessages] = useState<Row[]>([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [hydrated, setHydrated] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const username = getStoredUsername() ?? 'there'

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, typing, scrollToBottom])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const { chat_history } = await saveUsername(username)
        if (cancelled) return
        const rows: Row[] = (chat_history ?? []).map((m: ChatHistoryItem) => ({
          id: id(),
          text: m.message,
          isUser: !m.is_bot,
        }))
        setMessages(rows)
      } catch {
        if (!cancelled) setMessages([])
      } finally {
        if (!cancelled) setHydrated(true)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [username])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text) return
    setInput('')
    setMessages((m) => [...m, { id: id(), text, isUser: true }])
    setTyping(true)
    try {
      const { response } = await sendChatMessage(username, text)
      setMessages((m) => [...m, { id: id(), text: response, isUser: false }])
    } catch {
      setMessages((m) => [
        ...m,
        { id: id(), text: "Sorry, I'm having connection issues. Try again!", isUser: false },
      ])
    } finally {
      setTyping(false)
    }
  }

  return (
    <div className="relative z-10 flex min-h-[calc(100vh-6rem)] items-center justify-center p-4">
      <div className="mx-auto w-full max-w-5xl">
        <div className="flex h-[88vh] flex-col overflow-hidden rounded-3xl border border-[#30363d] bg-[rgba(22,27,34,0.88)] shadow-2xl backdrop-blur-xl glow-py">
          <div className="header-py-gradient p-6 sm:p-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white drop-shadow-lg sm:text-4xl">
                  Tushar<span className="text-yellow-300">.</span>dev()
                </h1>
                <p className="mt-1 text-sm font-light text-white/90 sm:text-base">
                  Senior AI Engineer • Python • .Net • FastAPI • PyTorch • React JS • C#
                </p>
              </div>
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-yellow-400 to-amber-600 text-3xl font-black text-black shadow-2xl glow-py">
                λ
              </div>
            </div>
          </div>

          <div className="scrollbar-chat flex-1 space-y-6 overflow-y-auto p-6 sm:p-8">
            {!hydrated ? (
              <p className="text-center text-sm text-gray-400">Loading conversation…</p>
            ) : null}
            <IntroBubbles onOpenScore={() => setModalOpen(true)} />
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message-enter max-w-[85%] rounded-2xl px-5 py-3 break-words sm:max-w-md lg:max-w-lg ${
                  msg.isUser
                    ? 'ml-auto bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    : 'mr-auto bg-white/20 text-white backdrop-blur-sm'
                }`}
              >
                <LinkifyText text={msg.text} />
              </div>
            ))}
            {typing ? (
              <div className="mr-auto rounded-2xl bg-white/20 px-5 py-3 text-white backdrop-blur-sm">
                Tushar is typing<span className="animate-pulse">…</span>
              </div>
            ) : null}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-white/10 bg-black/50 p-5 sm:p-7">
            <form className="flex flex-col items-center gap-4 sm:flex-row" onSubmit={onSubmit}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    void onSubmit(e as unknown as React.FormEvent)
                  }
                }}
                placeholder="Ask me anything …"
                autoComplete="off"
                className="input-message min-w-0 flex-1 rounded-full border border-yellow-500/30 bg-white/[0.08] px-6 py-4 text-white outline-none transition placeholder:text-white/60 focus:border-[#FFD43B] focus:bg-white/[0.12] focus:shadow-[0_0_0_4px_rgba(255,212,59,0.2)]"
              />
              <button
                type="submit"
                className="shrink-0 transform rounded-full border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 px-10 py-4 font-bold text-black shadow-xl glow-py transition-all duration-300 hover:scale-105 hover:from-yellow-400 hover:to-amber-500 active:scale-95"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>

      <ResumeMatchModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}

function IntroBubbles({ onOpenScore }: { onOpenScore: () => void }) {
  return (
    <>
      <div className="text-center">
        <p className="inline-block rounded-full border border-yellow-500/20 bg-white/5 px-6 py-3 text-sm backdrop-blur">
          Hi! I&apos;m Tushar&apos;s AI assistant.
          <br />
          Ask about skills, projects, or type <strong className="text-yellow-400">&quot;resume&quot;</strong> for CV
        </p>
      </div>
      <div className="text-center">
        <p className="inline-block rounded-full border border-yellow-500/20 bg-white/5 px-6 py-3 text-sm backdrop-blur">
          Want to check how well your resume matches a job?
          <br className="sm:hidden" />
          Click{' '}
          <button
            type="button"
            onClick={onOpenScore}
            className="cursor-pointer font-bold text-yellow-400 underline hover:text-yellow-300"
          >
            here
          </button>
        </p>
      </div>
    </>
  )
}
