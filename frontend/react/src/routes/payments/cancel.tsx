import { createFileRoute, Link } from '@tanstack/react-router'
import { XCircle, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export const Route = createFileRoute('/payments/cancel')({
    component: PaymentCancelComponent,
})

function PaymentCancelComponent() {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                    <div className="flex flex-col items-center text-center">
                        {/* Cancel Icon */}
                        <div className="flex items-center justify-center w-16 h-16 mb-6 bg-orange-100 dark:bg-orange-900/30 rounded-full">
                            <XCircle className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                        </div>

                        {/* Cancel Message */}
                        <h1 className="text-2xl font-bold mb-2">Payment Cancelled</h1>
                        <p className="text-muted-foreground mb-6">
                            No worries! Your payment was cancelled and you haven't been charged.
                        </p>

                        {/* Info box */}
                        <div className="w-full bg-muted/50 rounded-lg p-4 mb-6">
                            <p className="text-sm text-muted-foreground">
                                You can try again whenever you're ready. Your account remains active with current access level.
                            </p>
                        </div>

                        {/* Action Buttons */}
                        <div className="w-full space-y-3">
                            <Button variant="outline" asChild className="w-full">
                                <Link to="/app">
                                    Go to Dashboard
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
