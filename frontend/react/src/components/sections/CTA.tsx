import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRight, Play, Users, Clock, Shield } from 'lucide-react'

function CTA() {
    const stats = [
        { icon: Users, value: '99.9%', label: 'Uptime' },
        { icon: Clock, value: '10k+', label: 'Companies' },
        { icon: Shield, value: '24/7', label: 'Support' }
    ]

    return (
        <section className="py-24 bg-background">
            <div className="container mx-auto px-4">
                <div className="grid gap-12 lg:grid-cols-2 items-center lg:gap-16">
                    {/* Visual Element */}
                    <div className="relative lg:order-1">
                        <Card className="overflow-hidden border-0 shadow-xl">
                            <CardContent className="p-0">
                                {/* Mock dashboard interface */}
                                <div className="bg-muted p-4">
                                    <div className="flex items-center space-x-2 mb-4">
                                        <div className="w-3 h-3 bg-red-500 rounded-full" />
                                        <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                                        <div className="w-3 h-3 bg-green-500 rounded-full" />
                                        <div className="flex-1 h-4 bg-muted-foreground/20 rounded ml-4" />
                                    </div>

                                    {/* Content blocks */}
                                    <div className="space-y-3">
                                        <div className="flex space-x-3">
                                            <div className="w-10 h-10 bg-emerald-500 rounded-lg" />
                                            <div className="flex-1 space-y-2">
                                                <div className="h-2 bg-muted-foreground/20 rounded w-3/4" />
                                                <div className="h-2 bg-muted-foreground/10 rounded w-1/2" />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-3 gap-2">
                                            <div className="h-12 bg-muted-foreground/10 rounded border border-emerald-500/30" />
                                            <div className="h-12 bg-muted-foreground/10 rounded" />
                                            <div className="h-12 bg-muted-foreground/10 rounded" />
                                        </div>

                                        <div className="h-16 bg-muted-foreground/10 rounded" />

                                        <div className="flex justify-between items-center">
                                            <div className="h-6 bg-emerald-500 rounded w-20" />
                                            <div className="h-4 bg-muted-foreground/20 rounded w-12" />
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Content */}
                    <div className="lg:order-2">
                        <h2 className="mb-6 text-3xl font-bold tracking-tight md:text-4xl lg:text-5xl">
                            Ready to Transform Your{' '}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400">
                                Business?
                            </span>
                        </h2>
                        <p className="mb-8 text-lg text-muted-foreground leading-relaxed md:text-xl">
                            Join thousands of companies already using FutureFlow to streamline
                            operations, boost productivity, and accelerate growth.
                        </p>

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-6 mb-8">
                            {stats.map((stat) => {
                                const IconComponent = stat.icon
                                return (
                                    <div key={stat.label} className="text-center">
                                        <div className="mb-1 text-2xl font-bold text-emerald-500">
                                            {stat.value}
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            {stat.label}
                                        </div>
                                    </div>
                                )
                            })}
                        </div>

                        {/* CTA Buttons */}
                        <div className="flex flex-col gap-4 sm:flex-row">
                            <Button size="lg" className="group">
                                Start Free Trial
                                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                            </Button>

                            <Button variant="outline" size="lg" className="group">
                                <Play className="mr-2 h-4 w-4" />
                                Book a Demo
                            </Button>
                        </div>

                        {/* Trust indicators */}
                        <div className="mt-8 pt-6 border-t border-border">
                            <p className="mb-3 text-sm text-muted-foreground">
                                Trusted by industry leaders
                            </p>
                            <div className="flex items-center space-x-4 opacity-60">
                                {[
                                    { name: 'TechCorp', width: 'w-12' },
                                    { name: 'InnovateLabs', width: 'w-16' },
                                    { name: 'FutureFlow', width: 'w-14' },
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
                </div>
            </div>
        </section>
    )
}

export default CTA
