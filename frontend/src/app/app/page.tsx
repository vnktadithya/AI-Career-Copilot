'use client'

import { useSessionBootstrap } from '@/hooks/UseSessionBootstrap'

export default function AppPage() {
    useSessionBootstrap()

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center">
            <p className="text-sm text-zinc-400">
                Preparing your workspace…
            </p>
        </div>
    )
}
