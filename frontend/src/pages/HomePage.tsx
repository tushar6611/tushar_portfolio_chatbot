import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { CONTACT, RESUME_URL, skillGroups, stats } from '../data/portfolio'

export function HomePage() {
  const { hash, pathname } = useLocation()

  useEffect(() => {
    if (hash === '#skills') {
      const el = document.getElementById('skills')
      if (el) {
        const t = window.setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 150)
        return () => window.clearTimeout(t)
      }
    }
  }, [hash, pathname])

  return (
    <>
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-black/90 via-[#0d1117]/80 to-transparent" />
        <div className="relative z-10 mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 lg:grid-cols-2">
          <div className="glass-card glow-py card-hover rounded-2xl border border-yellow-500/20 p-10 backdrop-blur-xl">
            <div className="mb-8 flex items-center space-x-6">
              <div className="flex h-28 w-28 items-center justify-center rounded-2xl bg-gradient-to-br from-yellow-400 to-amber-600 text-6xl font-black text-black shadow-2xl glow-py">
                T
              </div>
              <div>
                <h2 className="text-3xl font-black">Tushar Chowdhury</h2>
                <p className="flex items-center gap-2 text-lg font-bold text-yellow-400">
                  <span>Senior AI Engineer</span>
                  <span className="inline-block rounded-full border border-yellow-500/30 bg-yellow-500/20 px-4 py-1 text-sm font-medium text-yellow-300">
                    Full-Stack + ML
                  </span>
                </p>
                <p className="mt-1 text-[var(--color-text-muted)]">{CONTACT.location}</p>
              </div>
            </div>

            <div className="space-y-4 font-mono text-sm">
              <div className="flex items-center space-x-4">
                <PhoneIcon />
                <span>{CONTACT.phone}</span>
              </div>
              <div className="flex items-center space-x-4">
                <MailIcon />
                <span>{CONTACT.email}</span>
              </div>
              <div className="flex items-center space-x-4">
                <PinIcon />
                <span>{CONTACT.location}</span>
              </div>
            </div>

            <div className="mt-8 flex flex-wrap gap-4">
              <a
                href={RESUME_URL}
                target="_blank"
                rel="noopener noreferrer"
                download="Tushar_Chowdhury_Resume.pdf"
                className="btn-python inline-block rounded-lg border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 px-8 py-4 font-bold text-black shadow-xl glow-py transition-all duration-300 hover:scale-105 hover:from-yellow-400 hover:to-amber-500 active:scale-95"
              >
                Download Resume
              </a>
              <Link
                to="/chat"
                className="btn-python inline-block rounded-lg border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 px-8 py-4 font-bold text-black shadow-xl glow-py transition-all duration-300 hover:scale-105 hover:from-yellow-400 hover:to-amber-500 active:scale-95"
              >
                Chat with Me
              </Link>
            </div>
          </div>

          <div className="text-center lg:text-left">
            <h1 className="text-5xl leading-tight font-black md:text-7xl">
              <span className="text-[#FFD43B]">print(</span>
              <span>&quot;Hello, World!&quot;</span>
              <span className="text-[#FFD43B]">)</span>
              <br />
              <span className="text-4xl md:text-6xl">I&apos;m Tushar</span>
            </h1>
            <p className="mt-6 max-w-2xl text-xl font-light text-[#8b949e]">
              Building production-grade AI systems, scalable microservices, and full-stack applications
              <br />
              with <strong className="text-white">.NET Core • Python • React • Next.js • Azure • AWS</strong>
            </p>
            <div className="mt-10 flex flex-wrap justify-center gap-6 lg:justify-start">
              <a
                href="#skills"
                className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-8 py-4 backdrop-blur transition hover:bg-yellow-500/20"
              >
                Explore Skills
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 text-center md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-5xl font-black text-yellow-400">{s.value}</div>
              <div className="text-[#8b949e]">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="skills" className="scroll-mt-28 px-6 py-20">
        <div className="mx-auto max-w-6xl text-center">
          <h2 className="section-title mb-4 text-4xl font-black tracking-tight text-transparent md:text-5xl">
            Core Expertise
          </h2>
          <style>{`
            .section-title {
              background: linear-gradient(90deg, #FFD43B, #FF8C00);
              -webkit-background-clip: text;
              background-clip: text;
            }
            .glass-card {
              background: rgba(22, 27, 34, 0.88);
              backdrop-filter: blur(16px);
              border: 1px solid #30363d;
            }
            .card-hover {
              transition: all 0.4s ease;
            }
            .card-hover:hover {
              transform: translateY(-10px);
              box-shadow: 0 20px 40px rgba(255, 212, 59, 0.25);
            }
          `}</style>

          <div className="mt-16 grid grid-cols-1 gap-10 md:grid-cols-3">
            {skillGroups.map((g) => (
              <div
                key={g.title}
                className="glass-card card-hover glow-py rounded-2xl border border-yellow-500/20 p-8 backdrop-blur-xl"
              >
                <h3 className="mb-4 text-2xl font-black text-yellow-300">{g.title}</h3>
                <ul className="space-y-2 text-lg text-[#8b949e]">
                  {g.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-transparent to-black/70 px-6 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mb-8 text-5xl font-black text-yellow-400 md:text-6xl">Ready to build the future?</h2>
          <p className="mb-10 text-xl text-[#8b949e]">
            Let&apos;s discuss your next big project — AI, cloud, or full-stack.
          </p>
          <Link
            to="/chat"
            className="inline-block rounded-lg border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 px-12 py-5 text-xl font-bold text-black shadow-xl glow-py transition-all duration-300 hover:from-yellow-400 hover:to-amber-500"
          >
            Start Conversation
          </Link>
        </div>
      </section>
    </>
  )
}

function PhoneIcon() {
  return (
    <svg className="h-5 w-5 shrink-0 text-[#FFD43B]" fill="currentColor" viewBox="0 0 20 20">
      <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
    </svg>
  )
}

function MailIcon() {
  return (
    <svg className="h-5 w-5 shrink-0 text-[#FFD43B]" fill="currentColor" viewBox="0 0 20 20">
      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
    </svg>
  )
}

function PinIcon() {
  return (
    <svg className="h-5 w-5 shrink-0 text-[#FFD43B]" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
        clipRule="evenodd"
      />
    </svg>
  )
}
