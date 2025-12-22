'use client'

import { supabase } from '@/lib/supabaseClient'

export function OAuthButtons() {
    const signInWithProvider = async (provider: 'google' | 'github') => {
        await supabase.auth.signInWithOAuth({
            provider,
            options: {
                redirectTo: `${window.location.origin}/app`,
            },
        })
    }

    return (
        <div className="space-y-3">
            <button
                onClick={() => signInWithProvider('google')}
                className="
          w-full rounded-xl border border-white/10
          py-2.5 text-sm text-white
          hover:bg-white/5 transition
        "
            >
                Continue with Google
            </button>

            <button
                onClick={() => signInWithProvider('github')}
                className="
          w-full rounded-xl border border-white/10
          py-2.5 text-sm text-white
          hover:bg-white/5 transition
        "
            >
                Continue with GitHub
            </button>
        </div>
    )
}
