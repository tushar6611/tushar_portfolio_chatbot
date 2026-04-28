import { useEffect, useRef } from 'react'

class Particle {
  x = 0
  y = 0
  size = 0
  speedX = 0
  speedY = 0
  opacity = 0.3
  private canvas: HTMLCanvasElement

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.reset()
  }

  reset() {
    this.x = Math.random() * this.canvas.width
    this.y = Math.random() * this.canvas.height
    this.size = Math.random() * 3 + 1
    this.speedX = Math.random() * 0.6 - 0.3
    this.speedY = Math.random() * 0.6 - 0.3
    this.opacity = 0.3
  }

  update(mouse: { x: number; y: number }) {
    this.x += this.speedX
    this.y += this.speedY
    const dx = mouse.x - this.x
    const dy = mouse.y - this.y
    const dist = Math.hypot(dx, dy)
    if (dist < 160 && dist > 0) {
      const force = 160 / (dist * dist)
      this.speedX += dx * force * 0.0006
      this.speedY += dy * force * 0.0006
      this.opacity = Math.min(0.9, this.opacity + 0.02)
    } else {
      this.opacity = Math.max(0.2, this.opacity - 0.005)
    }
    if (this.x < 0 || this.x > this.canvas.width) this.speedX *= -1
    if (this.y < 0 || this.y > this.canvas.height) this.speedY *= -1
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = `rgba(255, 212, 59, ${this.opacity})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

export function ParticleCanvas() {
  const ref = useRef<HTMLCanvasElement>(null)
  const mouse = useRef({ x: 0, y: 0 })
  const particles = useRef<Particle[]>([])
  const raf = useRef<number>(0)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      particles.current = []
      const count = Math.min(100, Math.floor(window.innerWidth / 12))
      for (let i = 0; i < count; i++) {
        particles.current.push(new Particle(canvas))
      }
    }

    const onMove = (e: MouseEvent) => {
      mouse.current.x = e.clientX
      mouse.current.y = e.clientY
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      for (const p of particles.current) {
        p.update(mouse.current)
        p.draw(ctx)
      }
      raf.current = requestAnimationFrame(animate)
    }

    resize()
    window.addEventListener('resize', resize)
    window.addEventListener('mousemove', onMove)
    raf.current = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(raf.current)
    }
  }, [])

  return (
    <canvas
      ref={ref}
      className="pointer-events-none fixed inset-0 z-[1] h-full w-full"
      aria-hidden
    />
  )
}
