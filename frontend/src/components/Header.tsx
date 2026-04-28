import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

const navClass = ({ isActive }: { isActive: boolean }) =>
  [
    'rounded-full px-6 py-3 font-medium transition-all duration-300',
    isActive
      ? 'relative font-bold text-white after:absolute after:inset-x-6 after:bottom-2 after:h-1 after:rounded-full after:bg-[#FFD43B]'
      : 'text-gray-400 hover:text-white',
  ].join(' ')

export function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="fixed top-0 right-0 left-0 z-50 border-b border-white/5 bg-black/90 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-7xl items-center px-6 py-5">
        <Link to="/" className="group flex items-center space-x-4" onClick={() => setOpen(false)}>
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-yellow-400 to-amber-600 text-2xl font-black text-black shadow-2xl glow-py">
            T
          </div>
          <span className="text-2xl font-black tracking-tight">
            Tushar<span className="text-yellow-400">.</span>
          </span>
        </Link>

        <nav className="ml-20 hidden items-center space-x-8 md:flex">
          <NavLink to="/home" end={true} className={navClass}>
            Home
          </NavLink>
          <Link
            to="/home#skills"
            className="rounded-full px-6 py-3 font-medium text-gray-400 transition-all duration-300 hover:text-white"
          >
            Skills
          </Link>
        </nav>

        <div className="ml-auto hidden md:block">
          <Link
            to="/chat"
            className="inline-block transform rounded-full border border-yellow-400/50 bg-gradient-to-r from-yellow-500 to-amber-600 px-8 py-3.5 font-bold tracking-wide text-black shadow-2xl glow-py transition-all duration-300 hover:scale-105 hover:from-yellow-400 hover:to-amber-500 active:scale-95"
          >
            Chat with Me
          </Link>
        </div>

        <button
          type="button"
          className="ml-auto text-white md:hidden"
          aria-expanded={open}
          aria-label="Toggle menu"
          onClick={() => setOpen((v) => !v)}
        >
          <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {open ? (
        <div className="border-t border-white/10 bg-black/95 backdrop-blur-2xl md:hidden">
          <div className="space-y-4 px-8 py-6">
            <Link
              to="/home"
              className="block py-3 text-lg text-gray-300 hover:text-white"
              onClick={() => setOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/home#skills"
              className="block py-3 text-lg text-gray-300 hover:text-white"
              onClick={() => setOpen(false)}
            >
              Skills
            </Link>
            <Link
              to="/chat"
              className="block rounded-xl bg-gradient-to-r from-yellow-500 to-amber-600 py-4 text-center font-bold text-black"
              onClick={() => setOpen(false)}
            >
              Chat with Me
            </Link>
          </div>
        </div>
      ) : null}
    </header>
  )
}
