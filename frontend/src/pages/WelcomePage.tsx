import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { saveUsername } from '../api/client'
import { setStoredUsername } from '../lib/session'

export function WelcomePage() {
  const navigate = useNavigate()
  const [value, setValue] = useState('')
  const [error, setError] = useState(false)
  const [pending, setPending] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) {
      setError(true)
      return
    }
    setPending(true)
    setError(false)
    try {
      await saveUsername(trimmed)
      setStoredUsername(trimmed)
      navigate('/home', { replace: true })
    } catch {
      setStoredUsername(trimmed)
      navigate('/home', { replace: true })
    } finally {
      setPending(false)
    }
  }

  function skip() {
    setStoredUsername('there')
    void saveUsername('there').catch(() => {})
    navigate('/home', { replace: true })
  }

  return (
    <div className="relative z-10 flex min-h-[calc(100vh-6rem)] items-center justify-center px-4">
      <div className="card-glass glow-py w-full max-w-md rounded-3xl p-12 text-center shadow-2xl">
        <style>{`
          .card-glass {
            background: rgba(22, 27, 34, 0.88);
            backdrop-filter: blur(20px);
            border: 1px solid #30363d;
          }
        `}</style>
        <h1 className="mb-4 text-5xl font-black tracking-tight text-white sm:text-6xl">
          {'>>> '}
          <span className="text-[#FFD43B]">Welcome</span>
          <span className="text-[#FFD43B]">.</span>
        </h1>
        <p className="mb-10 text-lg font-light text-gray-400">Enter your name or email to continue</p>

        <form className="space-y-6" onSubmit={onSubmit}>
          <div>
            <input
              type="text"
              value={value}
              onChange={(e) => {
                setValue(e.target.value)
                setError(false)
              }}
              placeholder="you@example.com or John"
              autoComplete="off"
              className="input-username w-full rounded-full border border-yellow-500/30 bg-white/[0.08] px-6 py-4 text-[1.1rem] text-white outline-none transition placeholder:text-white/60 focus:border-[#FFD43B] focus:bg-white/[0.12] focus:shadow-[0_0_0_4px_rgba(255,212,59,0.2)]"
            />
            {error ? (
              <span className="mt-2 block text-sm text-red-400">Please enter a name/email to continue.</span>
            ) : null}
          </div>

          <button
            type="submit"
            disabled={pending}
            className="glow-py w-full transform rounded-full border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 py-5 text-xl font-bold text-black shadow-2xl transition-all duration-300 hover:scale-105 hover:from-yellow-400 hover:to-amber-500 active:scale-95 disabled:opacity-60"
          >
            {pending ? 'Continuing…' : 'Continue'}
          </button>

          <button
            type="button"
            onClick={skip}
            className="mt-4 block w-full text-sm text-yellow-400/80 underline transition hover:text-yellow-300"
          >
            Skip (Not recommended)
          </button>
        </form>
      </div>
    </div>
  )
}
