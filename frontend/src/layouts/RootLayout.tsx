import { Outlet } from 'react-router-dom'
import { Header } from '../components/Header'
import { ParticleCanvas } from '../components/ParticleCanvas'

export function RootLayout() {
  return (
    <>
      <ParticleCanvas />
      <Header />
      <main className="relative z-10 pt-24">
        <Outlet />
      </main>
    </>
  )
}
