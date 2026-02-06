import { createFileRoute, Link } from '@tanstack/react-router'
import { CheckCircle, ArrowRight, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export const Route = createFileRoute('/payments/success')({
    component: PaymentSuccessComponent,
})

function PaymentSuccessComponent() {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                    <div className="flex flex-col items-center text-center">
                        {/* Success Icon */}
                        <div className="flex items-center justify-center w-16 h-16 mb-6 bg-emerald-100 dark:bg-emerald-900/30 rounded-full">
                            <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                        </div>

                        {/* Success Message */}
                        <h1 className="text-2xl font-bold mb-2">Payment Successful</h1>
                        <p className="text-muted-foreground mb-6">
                            Your subscription is now active. You have full access to all features.
                        </p>

                        {/* Features unlocked */}
                        <div className="w-full bg-muted/50 rounded-lg p-4 mb-6">
                            <div className="flex items-center gap-2 text-sm font-medium mb-3">
                                <Sparkles className="w-4 h-4 text-emerald-500" />
                                <span>What's unlocked</span>
                            </div>
                            <ul className="space-y-2 text-sm text-muted-foreground text-left">
                                <li className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                                    Full access to all features
                                </li>
                                <li className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                                    Priority support
                                </li>
                                <li className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                                    7-day free trial included
                                </li>
                            </ul>
                        </div>

                        {/* Action Button */}
                        <Button asChild className="w-full">
                            <Link to="/app">
                                Go to Dashboard
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
