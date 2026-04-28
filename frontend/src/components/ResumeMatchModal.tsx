import { useCallback, useRef, useState } from 'react'
import { analyzeResumeStream } from '../api/client'

type Props = {
  open: boolean
  onClose: () => void
}

export function ResumeMatchModal({ open, onClose }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [progress, setProgress] = useState(0)
  const [busy, setBusy] = useState(false)
  const [analyzeLabel, setAnalyzeLabel] = useState('Analyze Match Score')
  const [result, setResult] = useState<{
    score: number
    matched: string[]
    missing: string[]
  } | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const reset = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setFile(null)
    setJobDescription('')
    setProgress(0)
    setBusy(false)
    setAnalyzeLabel('Analyze Match Score')
    setResult(null)
  }, [])

  if (!open) return null

  async function analyze() {
    if (!file || !jobDescription.trim()) {
      window.alert('Please upload your resume (PDF) and paste a job description.')
      return
    }
    abortRef.current?.abort()
    abortRef.current = new AbortController()
    setBusy(true)
    setResult(null)
    setProgress(0)
    setAnalyzeLabel('Analyzing…')

    try {
      await analyzeResumeStream(
        file,
        jobDescription.trim(),
        (obj) => {
          if (typeof obj.progress === 'number') {
            const p = Math.min(100, Math.round(obj.progress))
            setProgress(p)
            setAnalyzeLabel(p < 100 ? 'Analyzing…' : 'Analyze Match Score')
          }
          if (obj.progress === 100) {
            setResult({
              score: obj.final_score ?? 0,
              matched: obj.matched_skills ?? [],
              missing: obj.missing_skills ?? [],
            })
          }
        },
        abortRef.current.signal,
      )
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        window.alert((e as Error).message || 'Analysis failed.')
      }
    } finally {
      setBusy(false)
      setAnalyzeLabel('Analyze Match Score')
      abortRef.current = null
    }
  }

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-start justify-center overflow-auto bg-black/90 p-6 pt-20 backdrop-blur-2xl"
      role="dialog"
      aria-modal
      aria-labelledby="resume-modal-title"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="modal-glow relative mb-20 w-full max-w-2xl rounded-3xl border border-[#30363d] bg-[rgba(13,17,23,0.95)] p-8 shadow-2xl backdrop-blur-xl">
        <button
          type="button"
          className="absolute top-4 right-4 z-10 text-4xl text-gray-400 transition hover:text-yellow-400 sm:text-5xl"
          aria-label="Close"
          onClick={() => {
            reset()
            onClose()
          }}
        >
          ×
        </button>

        <h2 id="resume-modal-title" className="mb-6 text-2xl font-black text-yellow-400 sm:text-3xl">
          Resume Match Score
        </h2>

        <div className="space-y-6">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">Upload Resume (PDF)</label>
            <input
              type="file"
              accept="application/pdf"
              className="w-full cursor-pointer rounded-xl border border-yellow-500/30 bg-white/5 px-4 py-3 text-white file:mr-4 file:cursor-pointer file:rounded-full file:border-0 file:bg-gradient-to-r file:from-yellow-500 file:to-amber-600 file:px-6 file:py-2 file:font-bold file:text-black hover:file:from-yellow-400"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-300">Paste Job Description</label>
            <textarea
              rows={7}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="e.g. Looking for a Senior Python Developer with FastAPI, Docker, and ML experience…"
              className="w-full resize-none rounded-xl border border-yellow-500/30 bg-white/5 px-4 py-3 font-light text-white placeholder:text-gray-500 focus:border-yellow-400 focus:ring-4 focus:ring-yellow-400/30 focus:outline-none"
            />
          </div>

          <button
            type="button"
            disabled={busy}
            onClick={() => void analyze()}
            className="relative w-full cursor-pointer overflow-hidden rounded-full bg-gradient-to-r from-yellow-500 to-amber-600 py-4 font-bold text-black shadow-[0_0_40px_rgba(255,212,59,0.6)] transition hover:scale-[1.02] hover:from-yellow-400 hover:to-amber-500 active:scale-[0.98] disabled:opacity-60"
          >
            <span
              className="absolute top-0 left-0 h-full rounded-full bg-white/25 transition-[width] duration-300"
              style={{ width: `${progress}%` }}
            />
            <span className="relative z-10">{analyzeLabel}</span>
          </button>

          {result ? (
            <div className="mt-6 rounded-2xl border border-yellow-500/20 bg-white/5 p-6">
              <h3 className="mb-4 text-2xl font-bold text-yellow-400">Match Score</h3>
              <p className="mb-6 text-7xl font-extrabold text-yellow-400">{result.score}%</p>
              <div className="grid grid-cols-1 gap-6 text-sm md:grid-cols-3">
                <SkillColumn title="Matched Skills" titleClass="text-green-400" items={result.matched} />
                <SkillColumn title="Missing Skills" titleClass="text-orange-400" items={result.missing} />
                <SkillColumn
                  title="Suggestions"
                  titleClass="text-cyan-400"
                  items={result.missing.slice(0, 15)}
                  emptyHint="Add missing keywords to your resume where truthful."
                />
              </div>
            </div>
          ) : null}

          <button
            type="button"
            className="mt-4 w-full rounded-xl border border-yellow-500/20 bg-white/5 py-4 font-medium text-gray-300 transition hover:bg-white/10 hover:text-white"
            onClick={reset}
          >
            Clear & Start Over
          </button>
        </div>
      </div>
    </div>
  )
}

function SkillColumn({
  title,
  titleClass,
  items,
  emptyHint,
}: {
  title: string
  titleClass: string
  items: string[]
  emptyHint?: string
}) {
  const show = items.length ? items.slice(0, 15) : []
  return (
    <div>
      <h4 className={`mb-3 font-bold ${titleClass}`}>{title}</h4>
      <ul className="ml-5 list-disc space-y-1 text-gray-300">
        {show.length ? (
          show.map((item) => (
            <li key={item} className="leading-relaxed">
              {item}
            </li>
          ))
        ) : (
          <li className="text-gray-500 italic">{emptyHint ?? 'None detected'}</li>
        )}
      </ul>
    </div>
  )
}
