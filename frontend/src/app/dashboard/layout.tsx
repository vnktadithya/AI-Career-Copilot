'use client'

import { useSessionBootstrap } from '@/hooks/UseSessionBootstrap'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    useSessionBootstrap()

    return <>{children}</>
}
