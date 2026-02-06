import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Play } from 'lucide-react'

function Hero() {
    const [currentText, setCurrentText] = useState(0)
    const heroTexts = [
        "Build the future today",
        "Transform your business",
        "Accelerate innovation"
    ]

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentText((prev) => (prev + 1) % heroTexts.length)
        }, 3000)
        return () => clearInterval(interval)
    }, [])

    return (
        <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/20">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-20 left-20 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl animate-pulse-slow delay-1000" />
            </div>

            <div className="relative z-10 container mx-auto px-4 text-center">
                {/* Announcement Badge */}
                <div className="inline-flex items-center gap-2 mb-8 px-4 py-2 text-sm bg-muted border rounded-lg">
                    <Badge variant="secondary" className="bg-emerald-500 text-white">
                        New
                    </Badge>
                    <span className="text-sm font-medium">Professional solutions for modern businesses</span>
                    <ArrowRight className="w-4 h-4" />
                </div>

                {/* Main Heading */}
                <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl lg:text-7xl animate-slide-up">
                    <span className="block">{heroTexts[currentText].split(' ').slice(0, -1).join(' ')}</span>
                    <span className="block text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400 animate-pulse-slow">
                        {heroTexts[currentText].split(' ').slice(-1)}
                    </span>
                </h1>

                {/* Subtitle */}
                <p className="mx-auto mb-10 max-w-3xl text-xl font-light text-muted-foreground leading-relaxed md:text-2xl">
                    Transform your business with cutting-edge solutions designed for
                    tomorrow's challenges. Innovation meets reliability.
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col gap-4 sm:flex-row sm:justify-center sm:gap-6 mb-16 animate-fade-in">
                    <Button size="lg" className="group animate-bounce-gentle">
                        Get Started
                        <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                    <Button variant="outline" size="lg" className="group">
                        <Play className="mr-2 h-4 w-4" />
                        Go to Demo
                    </Button>
                </div>

                {/* Trust Indicators */}
                <div className="mx-auto max-w-4xl">
                    <p className="mb-8 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                        Trusted by leading companies
                    </p>
                    <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
                        {[
                            { name: 'TechCorp', width: 'w-16' },
                            { name: 'InnovateLabs', width: 'w-20' },
                            { name: 'FutureFlow', width: 'w-18' },
                            { name: 'NextGen', width: 'w-16' },
                        ].map((company) => (
                            <div
                                key={company.name}
                                className={`${company.width} h-6 bg-muted-foreground/20 rounded`}
                                aria-label={`${company.name} logo`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}

export default Hero
