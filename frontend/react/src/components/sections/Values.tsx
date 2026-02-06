import { Card, CardContent } from '@/components/ui/card'
import { Star, Zap, Code, Shield } from 'lucide-react'

const values = [
    {
        icon: Star,
        title: "Excellence",
        description: "Committed to delivering world-class solutions",
        color: "bg-emerald-500"
    },
    {
        icon: Zap,
        title: "Speed",
        description: "Rapid iteration and deployment",
        color: "bg-blue-500"
    },
    {
        icon: Code,
        title: "Innovation",
        description: "Cutting-edge technology solutions",
        color: "bg-purple-500"
    },
    {
        icon: Shield,
        title: "Quality",
        description: "Built to last with rigorous testing",
        color: "bg-orange-500"
    }
]

function Values() {
    return (
        <section className="relative py-24 bg-background">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-10 left-10 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl" />
                <div className="absolute bottom-10 right-10 w-72 h-72 bg-teal-500/5 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 container mx-auto px-4">
                <div className="grid gap-16 lg:grid-cols-2 items-center">
                    {/* Content */}
                    <div className="lg:order-1">
                        <h2 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
                            Innovation meets{' '}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400">
                                execution
                            </span>
                        </h2>
                        <p className="mb-6 text-lg leading-relaxed text-muted-foreground">
                            We're builders, innovators, and problem-solvers. Our team combines strategic thinking with cutting-edge
                            technology to deliver solutions that scale with your ambitions.
                        </p>
                        <p className="mb-8 text-lg leading-relaxed text-muted-foreground">
                            From startups to enterprise, we bring the perfect balance of agility and expertise to transform your vision
                            into reality.
                        </p>

                        {/* Value indicators */}
                        <div className="flex flex-wrap gap-4">
                            {values.map((value) => {
                                const IconComponent = value.icon
                                return (
                                    <div key={value.title} className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-emerald-500 rounded-full" />
                                        <span className="font-medium text-foreground">{value.title}</span>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                    {/* Visual Grid */}
                    <div className="grid grid-cols-2 gap-4 lg:order-2">
                        <div className="space-y-4">
                            <Card className="group p-6 border-0 bg-gradient-to-br from-emerald-500/10 to-teal-400/5 shadow-lg hover:shadow-xl transition-all duration-300">
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500">
                                    <Star className="h-6 w-6 text-white" />
                                </div>
                                <h4 className="mb-2 font-semibold text-foreground">Excellence</h4>
                                <p className="text-sm text-muted-foreground">Committed to delivering world-class solutions</p>
                            </Card>

                            <Card className="group p-6 border-0 bg-muted shadow-lg hover:shadow-xl transition-all duration-300">
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400">
                                    <Zap className="h-6 w-6 text-white" />
                                </div>
                                <h4 className="mb-2 font-semibold text-foreground">Speed</h4>
                                <p className="text-sm text-muted-foreground">Rapid iteration and deployment</p>
                            </Card>
                        </div>

                        <div className="space-y-4 mt-8">
                            <Card className="group p-6 border-0 bg-muted shadow-lg hover:shadow-xl transition-all duration-300">
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400">
                                    <Code className="h-6 w-6 text-white" />
                                </div>
                                <h4 className="mb-2 font-semibold text-foreground">Innovation</h4>
                                <p className="text-sm text-muted-foreground">Cutting-edge technology solutions</p>
                            </Card>

                            <Card className="group p-6 border-0 bg-gradient-to-br from-emerald-500/10 to-teal-400/5 shadow-lg hover:shadow-xl transition-all duration-300">
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500">
                                    <Shield className="h-6 w-6 text-white" />
                                </div>
                                <h4 className="mb-2 font-semibold text-foreground">Quality</h4>
                                <p className="text-sm text-muted-foreground">Built to last with rigorous testing</p>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default Values
