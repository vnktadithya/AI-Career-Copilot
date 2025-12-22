'use client'

import { AuthCard } from '@//components/auth/AuthCard'
import { OAuthButtons } from '@//components/auth/OAuthButtons'
import { AuthFooter } from '@//components/auth/AuthFooter'
import { supabase } from '@/lib/supabaseClient'
import { useState } from 'react'

export default function SignupPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [username, setUsername] = useState('')
    const [error, setError] = useState<string | null>(null)

    const handleSignup = async () => {
        setError(null)

        const { error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    username,
                },
            },
        })

        if (error) {
            setError(error.message)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-zinc-900 to-black px-4">
            <AuthCard>
                <h1 className="text-2xl font-semibold tracking-tight mb-1">
                    Create your account
                </h1>
                <p className="text-sm text-zinc-400 mb-6">
                    Start building your professional narrative.
                </p>

                <div className="space-y-4">
                    <input
                        type="text"
                        placeholder="Username"
                        className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />

                    <input
                        type="email"
                        placeholder="Email"
                        className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    {error && (
                        <p className="text-sm text-red-400">{error}</p>
                    )}

                    <button
                        onClick={handleSignup}
                        className="
                w-full rounded-xl bg-white text-black
                py-2.5 text-sm font-medium
                hover:opacity-90 transition
            "
                    >
                        Sign up
                    </button>
                </div>

                <div className="my-6 border-t border-white/10" />

                <OAuthButtons />

                <AuthFooter
                    text="Already have an account?"
                    linkText="Sign in"
                    href="/auth/login"
                />
            </AuthCard>
        </div>
    )
}
