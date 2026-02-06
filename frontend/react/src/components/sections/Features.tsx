import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
    BarChart3,
    Shield,
    Zap,
    DollarSign,
    Palette,
    Settings
} from 'lucide-react'

const features = [
    {
        icon: BarChart3,
        title: "Smart Analytics",
        description: "Advanced insights and real-time analytics to drive data-driven decisions and optimize your marketing campaigns.",
        color: "bg-emerald-500"
    },
    {
        icon: Shield,
        title: "Enterprise Security",
        description: "Military-grade encryption and compliance frameworks to protect your organization's most sensitive data.",
        color: "bg-blue-500"
    },
    {
        icon: Zap,
        title: "AI Automation",
        description: "Intelligent workflows that adapt to your business needs, reducing manual tasks by up to 80%.",
        color: "bg-yellow-500"
    },
    {
        icon: DollarSign,
        title: "Smart Finance",
        description: "Automated financial operations with real-time reporting, forecasting, and compliance monitoring.",
        color: "bg-green-500"
    },
    {
        icon: Palette,
        title: "Design System",
        description: "Comprehensive design tools and component libraries for consistent, beautiful user experiences.",
        color: "bg-purple-500"
    },
    {
        icon: Settings,
        title: "Operations Hub",
        description: "Centralized command center for monitoring, managing, and optimizing all your business operations.",
        color: "bg-orange-500"
    }
]

function Features() {
    return (
        <section id="features" className="py-24 bg-muted/30">
            <div className="container mx-auto px-4">
                {/* Section Header */}
                <div className="mx-auto max-w-3xl text-center mb-16">
                    <h2 className="mb-6 text-3xl font-bold tracking-tight md:text-4xl lg:text-5xl">
                        Powerful Features for{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400">
                            Modern Teams
                        </span>
                    </h2>
                    <p className="text-lg text-muted-foreground leading-relaxed">
                        Streamline your workflow with intelligent automation and
                        cutting-edge tools designed for peak performance.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {features.map((feature, index) => {
                        const IconComponent = feature.icon
                        return (
                            <Card
                                key={feature.title}
                                className="group relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                            >
                                <CardHeader className="pb-4">
                                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                                        <IconComponent className="h-6 w-6 text-foreground" />
                                    </div>
                                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-muted-foreground leading-relaxed">
                                        {feature.description}
                                    </p>
                                </CardContent>

                                {/* Hover effect */}
                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-400/5 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            </Card>
                        )
                    })}
                </div>
            </div>
        </section>
    )
}

export default Features
