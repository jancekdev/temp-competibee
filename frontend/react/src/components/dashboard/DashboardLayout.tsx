import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Plus, CheckCircle, Circle, Edit, Trash2, Home, LogOut, User, Moon, Sun, ShieldCheck, CreditCard, Bug } from 'lucide-react'
import { getCSRFToken } from '@/lib/cookies'

interface Todo {
    id: number
    title: string
    description: string
    completed: boolean
    created_at: string
    updated_at: string
}

interface User {
    id: number
    email: string
    name: string
    has_membership: boolean
    membership_paused: boolean
}

export function DashboardLayout() {
    const [activeTab, setActiveTab] = useState('dashboard')
    const [isDark, setIsDark] = useState(false)
    const [user, setUser] = useState<User | null>(null)
    const [todos, setTodos] = useState<Todo[]>([])
    const [newTodo, setNewTodo] = useState({ title: '', description: '' })
    const [editingTodo, setEditingTodo] = useState<Todo | null>(null)
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
    const [loading, setLoading] = useState(false)

    const toggleTheme = () => {
        setIsDark(!isDark)
        document.documentElement.classList.toggle('dark')
    }

    // Fetch user and todos from Django API
    useEffect(() => {
        fetchUser()
        fetchTodos()
    }, [])

    const fetchUser = async () => {
        try {
            const response = await fetch('/api/user/', {
                credentials: 'include',
            })
            if (response.ok) {
                const userData = await response.json()
                setUser(userData)
            } else {
                console.error('Failed to fetch user:', response.status)
            }
        } catch (error) {
            console.error('Error fetching user:', error)
        }
    }

    const fetchTodos = async () => {
        try {
            const response = await fetch('/api/todos/', {
                credentials: 'include',
            })
            if (response.ok) {
                const data = await response.json()
                setTodos(data)
            } else {
                console.error('Failed to fetch todos:', response.status)
            }
        } catch (error) {
            console.error('Error fetching todos:', error)
        }
    }

    const createTodo = async () => {
        if (!newTodo.title.trim()) return

        setLoading(true)
        try {
            const csrfToken = getCSRFToken()
            const response = await fetch('/api/todos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
                body: JSON.stringify({
                    title: newTodo.title,
                    description: newTodo.description,
                    completed: false,
                }),
            })

            if (response.ok) {
                const createdTodo = await response.json()
                setTodos([createdTodo, ...todos])
                setNewTodo({ title: '', description: '' })
                setIsCreateDialogOpen(false)
            } else {
                console.error('Failed to create todo:', response.status)
            }
        } catch (error) {
            console.error('Error creating todo:', error)
        } finally {
            setLoading(false)
        }
    }

    const updateTodo = async (todo: Todo) => {
        setLoading(true)
        try {
            const csrfToken = getCSRFToken()
            const response = await fetch(`/api/todos/${todo.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
                body: JSON.stringify({
                    title: todo.title,
                    description: todo.description,
                    completed: todo.completed,
                }),
            })

            if (response.ok) {
                const updatedTodo = await response.json()
                setTodos(todos.map(t => t.id === updatedTodo.id ? updatedTodo : t))
                setEditingTodo(null)
                setIsEditDialogOpen(false)
            } else {
                console.error('Failed to update todo:', response.status)
            }
        } catch (error) {
            console.error('Error updating todo:', error)
        } finally {
            setLoading(false)
        }
    }

    const toggleComplete = async (todo: Todo) => {
        await updateTodo({ ...todo, completed: !todo.completed })
    }

    const deleteTodo = async (id: number) => {
        setLoading(true)
        try {
            const csrfToken = getCSRFToken()
            const response = await fetch(`/api/todos/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
            })

            if (response.ok) {
                setTodos(todos.filter(t => t.id !== id))
            } else {
                console.error('Failed to delete todo:', response.status)
            }
        } catch (error) {
            console.error('Error deleting todo:', error)
        } finally {
            setLoading(false)
        }
    }

    const completedCount = todos.filter(t => t.completed).length
    const totalCount = todos.length

    const handleLogout = async () => {
        try {
            const csrfToken = getCSRFToken()

            // Create a form and submit it to handle Django allauth logout properly
            const form = document.createElement('form')
            form.method = 'POST'
            form.action = '/accounts/logout/'
            form.style.display = 'none'

            const csrfInput = document.createElement('input')
            csrfInput.type = 'hidden'
            csrfInput.name = 'csrfmiddlewaretoken'
            csrfInput.value = csrfToken

            form.appendChild(csrfInput)
            document.body.appendChild(form)
            form.submit()
        } catch (error) {
            console.error('Error during logout:', error)
            // Fallback: redirect to logout page
            window.location.href = '/accounts/logout/'
        }
    }

    const handleCancelAccess = async () => {
        try {
            const csrfToken = getCSRFToken()
            const response = await fetch('/api/debug/cancel-access/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
            })
            if (response.ok) {
                fetchUser()
            } else {
                console.error('Failed to cancel access:', response.status)
            }
        } catch (error) {
            console.error('Error cancelling access:', error)
        }
    }

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <div className="w-64 border-r bg-muted/30 p-6">
                <div className="space-y-6">
                    <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-emerald-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">Q</span>
                        </div>
                        <span className="font-bold text-lg">Dashboard</span>
                    </div>

                    <nav className="space-y-2">
                        <Button
                            variant={activeTab === 'dashboard' ? 'secondary' : 'ghost'}
                            className="w-full justify-start"
                            onClick={() => setActiveTab('dashboard')}
                        >
                            <Home className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                        <Button
                            variant={activeTab === 'todos' ? 'secondary' : 'ghost'}
                            className="w-full justify-start"
                            onClick={() => setActiveTab('todos')}
                        >
                            <CheckCircle className="mr-2 h-4 w-4" />
                            Todos
                        </Button>
                        <Button
                            variant="ghost"
                            className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                            onClick={handleLogout}
                        >
                            <LogOut className="mr-2 h-4 w-4" />
                            Logout
                        </Button>
                    </nav>

                    <div className="pt-6 border-t space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Theme</span>
                            <div className="flex items-center space-x-2">
                                <Sun className="h-4 w-4" />
                                <Switch checked={isDark} onCheckedChange={toggleTheme} />
                                <Moon className="h-4 w-4" />
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="h-8 w-8 bg-muted rounded-full flex items-center justify-center">
                                <User className="h-4 w-4" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">{user?.name || 'Loading...'}</p>
                                <p className="text-xs text-muted-foreground">{user?.email || ''}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <h1 className="text-2xl font-bold">
                            {activeTab === 'dashboard' && 'Dashboard Overview'}
                            {activeTab === 'todos' && 'Todo Management'}
                        </h1>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <Sun className="h-4 w-4" />
                                <Switch checked={isDark} onCheckedChange={toggleTheme} />
                                <Moon className="h-4 w-4" />
                            </div>
                            {activeTab === 'todos' && (
                                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button>
                                            <Plus className="mr-2 h-4 w-4" />
                                            New Todo
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>Create New Todo</DialogTitle>
                                        </DialogHeader>
                                        <div className="space-y-4">
                                            <div>
                                                <Label htmlFor="title">Title</Label>
                                                <Input
                                                    id="title"
                                                    value={newTodo.title}
                                                    onChange={(e) => setNewTodo({ ...newTodo, title: e.target.value })}
                                                    placeholder="Enter todo title"
                                                    disabled={loading}
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="description">Description</Label>
                                                <Textarea
                                                    id="description"
                                                    value={newTodo.description}
                                                    onChange={(e) => setNewTodo({ ...newTodo, description: e.target.value })}
                                                    placeholder="Enter todo description"
                                                    rows={3}
                                                    disabled={loading}
                                                />
                                            </div>
                                            <div className="flex justify-end space-x-2">
                                                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)} disabled={loading}>
                                                    Cancel
                                                </Button>
                                                <Button onClick={createTodo} disabled={loading || !newTodo.title.trim()}>
                                                    {loading ? 'Creating...' : 'Create'}
                                                </Button>
                                            </div>
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            )}
                        </div>
                    </div>

                    {/* Dashboard Content */}
                    {activeTab === 'dashboard' && (
                        <div className="space-y-6">
                            {/* Stats Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Total Todos</CardTitle>
                                        <CheckCircle className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold">{totalCount}</div>
                                        <p className="text-xs text-muted-foreground">
                                            {completedCount} completed
                                        </p>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
                                        <Badge variant="secondary">
                                            {totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0}%
                                        </Badge>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold">
                                            {completedCount}/{totalCount}
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            todos completed
                                        </p>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
                                        <Circle className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold">
                                            {totalCount - completedCount}
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            remaining tasks
                                        </p>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Recent Todos */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Recent Todos</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {todos.slice(0, 5).map((todo) => (
                                            <div key={todo.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => toggleComplete(todo)}
                                                    disabled={loading}
                                                >
                                                    {todo.completed ? (
                                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                                    ) : (
                                                        <Circle className="h-4 w-4" />
                                                    )}
                                                </Button>
                                                <div className="flex-1">
                                                    <h4 className={`font-medium ${todo.completed ? 'line-through text-muted-foreground' : ''}`}>
                                                        {todo.title}
                                                    </h4>
                                                    {todo.description && (
                                                        <p className="text-sm text-muted-foreground">{todo.description}</p>
                                                    )}
                                                </div>
                                                <Badge variant={todo.completed ? 'secondary' : 'default'}>
                                                    {todo.completed ? 'Done' : 'Active'}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Access Card */}
                            <Card className="mt-6">
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        {user?.has_membership && !user?.membership_paused ? (
                                            <>
                                                <ShieldCheck className="h-5 w-5 text-emerald-500" />
                                                Access Status
                                            </>
                                        ) : (
                                            <>
                                                <CreditCard className="h-5 w-5" />
                                                Get Access
                                            </>
                                        )}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {user?.has_membership && !user?.membership_paused ? (
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                                                    <ShieldCheck className="h-5 w-5" />
                                                    <span className="font-medium">You have full access</span>
                                                </div>
                                                <Button variant="outline" asChild>
                                                    <a href="/payments/customer-portal/">
                                                        Manage Subscription
                                                    </a>
                                                </Button>
                                            </div>
                                            <div className="pt-3 border-t border-dashed">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2 text-muted-foreground text-sm">
                                                        <Bug className="h-4 w-4" />
                                                        <span>Debug only</span>
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                                                        onClick={handleCancelAccess}
                                                    >
                                                        Cancel Access
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            <p className="text-muted-foreground">
                                                Purchase access to unlock all features.
                                            </p>
                                            <Button asChild>
                                                {/* TODO: Replace YOUR_STRIPE_PRICE_ID with your actual Stripe price ID */}
                                                <a href="/payments/checkout/YOUR_STRIPE_PRICE_ID">
                                                    <CreditCard className="mr-2 h-4 w-4" />
                                                    Purchase Access
                                                </a>
                                            </Button>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Todos Content */}
                    {activeTab === 'todos' && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Todo List</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Title</TableHead>
                                            <TableHead>Description</TableHead>
                                            <TableHead>Created</TableHead>
                                            <TableHead>Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {todos.map((todo) => (
                                            <TableRow key={todo.id}>
                                                <TableCell>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => toggleComplete(todo)}
                                                        disabled={loading}
                                                    >
                                                        {todo.completed ? (
                                                            <CheckCircle className="h-4 w-4 text-green-500" />
                                                        ) : (
                                                            <Circle className="h-4 w-4" />
                                                        )}
                                                    </Button>
                                                </TableCell>
                                                <TableCell className="font-medium">
                                                    <span className={todo.completed ? 'line-through text-muted-foreground' : ''}>
                                                        {todo.title}
                                                    </span>
                                                </TableCell>
                                                <TableCell className="max-w-xs truncate">
                                                    {todo.description}
                                                </TableCell>
                                                <TableCell className="text-sm text-muted-foreground">
                                                    {new Date(todo.created_at).toLocaleDateString()}
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex space-x-2">
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => {
                                                                setEditingTodo(todo)
                                                                setIsEditDialogOpen(true)
                                                            }}
                                                            disabled={loading}
                                                        >
                                                            <Edit className="h-4 w-4" />
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => deleteTodo(todo.id)}
                                                            disabled={loading}
                                                        >
                                                            <Trash2 className="h-4 w-4 text-red-500" />
                                                        </Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>

                                {todos.length === 0 && (
                                    <div className="text-center py-8 text-muted-foreground">
                                        No todos yet. Create your first todo using the "New Todo" button above!
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}


                    {/* Edit Dialog */}
                    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Edit Todo</DialogTitle>
                            </DialogHeader>
                            {editingTodo && (
                                <div className="space-y-4">
                                    <div>
                                        <Label htmlFor="edit-title">Title</Label>
                                        <Input
                                            id="edit-title"
                                            value={editingTodo.title}
                                            onChange={(e) => setEditingTodo({ ...editingTodo, title: e.target.value })}
                                            disabled={loading}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="edit-description">Description</Label>
                                        <Textarea
                                            id="edit-description"
                                            value={editingTodo.description}
                                            onChange={(e) => setEditingTodo({ ...editingTodo, description: e.target.value })}
                                            rows={3}
                                            disabled={loading}
                                        />
                                    </div>
                                    <div className="flex justify-end space-x-2">
                                        <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={loading}>
                                            Cancel
                                        </Button>
                                        <Button onClick={() => updateTodo(editingTodo)} disabled={loading}>
                                            {loading ? 'Saving...' : 'Save Changes'}
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </DialogContent>
                    </Dialog>
                </div>
            </div>
        </div>
    )
}