import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check } from 'lucide-react'

const plans = [
    {
        name: 'Starter',
        price: 29,
        description: 'Perfect for small teams and individual projects.',
        features: [
            'Custom configuration',
            'No setup fees',
            'Up to 5 team members',
            'Email support',
            'Regular updates'
        ],
        cta: 'Get Started',
        variant: 'outline' as const
    },
    {
        name: 'Business',
        price: 99,
        description: 'Ideal for growing teams and businesses.',
        features: [
            'Advanced configuration',
            'Priority onboarding',
            'Up to 25 team members',
            'Priority support',
            'Advanced analytics'
        ],
        cta: 'Start Free Trial',
        variant: 'default' as const,
        popular: true
    },
    {
        name: 'Enterprise',
        price: 499,
        description: 'Custom solutions for large organizations.',
        features: [
            'Custom deployment',
            'Dedicated success manager',
            'Unlimited team members',
            '24/7 premium support',
            'Custom integrations'
        ],
        cta: 'Contact Sales',
        variant: 'outline' as const
    }
]

function Pricing() {
    const [isAnnual, setIsAnnual] = useState(false)

    const getPrice = (price: number) => {
        return isAnnual ? Math.round(price * 12 * 0.8) : price
    }

    return (
        <section id="pricing" className="py-24 bg-muted/30">
            <div className="container mx-auto px-4">
                {/* Section Header */}
                <div className="mx-auto max-w-3xl text-center mb-16">
                    <h2 className="mb-6 text-3xl font-bold tracking-tight md:text-4xl lg:text-5xl">
                        Choose Your{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400">
                            Perfect Plan
                        </span>
                    </h2>
                    <p className="mb-8 text-lg text-muted-foreground leading-relaxed">
                        Scale your business with flexible pricing designed to grow with you.
                        No hidden fees, cancel anytime.
                    </p>

                    {/* Billing Toggle */}
                    <div className="flex items-center justify-center space-x-4">
                        <span className={!isAnnual ? 'font-semibold text-foreground' : 'text-muted-foreground'}>
                            Monthly
                        </span>
                        <button
                            onClick={() => setIsAnnual(!isAnnual)}
                            className="relative inline-flex h-6 w-11 items-center rounded-full bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                        >
                            <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-emerald-500 transition-transform ${isAnnual ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                            />
                        </button>
                        <span className={isAnnual ? 'font-semibold text-foreground' : 'text-muted-foreground'}>
                            Annual
                        </span>
                        <Badge variant="secondary" className="bg-emerald-500 text-white">
                            Save 20%
                        </Badge>
                    </div>
                </div>

                {/* Pricing Cards */}
                <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
                    {plans.map((plan) => (
                        <Card
                            key={plan.name}
                            className={`relative flex flex-col ${plan.popular
                                ? 'border-2 border-emerald-500 shadow-lg scale-105'
                                : 'border shadow-sm hover:shadow-md'
                                } transition-all duration-300`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                                    <Badge className="bg-emerald-500 text-white">
                                        Most Popular
                                    </Badge>
                                </div>
                            )}

                            <CardHeader className="text-center pb-4">
                                <h3 className="text-2xl font-bold">{plan.name}</h3>
                                <p className="text-muted-foreground mt-2">{plan.description}</p>

                                <div className="mt-4">
                                    <span className="text-5xl font-bold text-emerald-500">
                                        ${getPrice(plan.price)}
                                    </span>
                                    <span className="text-muted-foreground">/{isAnnual ? 'year' : 'month'}</span>
                                </div>
                            </CardHeader>

                            <CardContent className="flex-1">
                                <ul className="space-y-4 mb-8">
                                    {plan.features.map((feature) => (
                                        <li key={feature} className="flex items-center space-x-3">
                                            <div className="flex-shrink-0 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                                                <Check className="w-3 h-3 text-white" />
                                            </div>
                                            <span className="text-sm text-foreground">{feature}</span>
                                        </li>
                                    ))}
                                </ul>

                                <Button
                                    className="w-full"
                                    variant={plan.variant}
                                    size="lg"
                                >
                                    {plan.cta}
                                </Button>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </section>
    )
}

export default Pricing
