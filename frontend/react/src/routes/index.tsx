import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import Header from '@/components/Header'
import Hero from '@/components/sections/Hero'
import Features from '@/components/sections/Features'
import Values from '@/components/sections/Values'
import Pricing from '@/components/sections/Pricing'
import CTA from '@/components/sections/CTA'
import { getSeoMeta, siteConfig } from '@/lib/seo'

export const Route = createFileRoute('/')({
  head: () => ({
    meta: getSeoMeta(),
    links: [{ rel: 'canonical', href: siteConfig.url }],
  }),
  component: LandingPage,
})

function LandingPage() {
  const [isDark, setIsDark] = useState(false)

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header isDark={isDark} toggleTheme={toggleTheme} />
      <main>
        <Hero />
        <Features />
        <Values />
        <Pricing />
        <CTA />
      </main>
    </div>
  )
}
