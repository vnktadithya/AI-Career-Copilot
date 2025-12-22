'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { api } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'

export function useSessionBootstrap() {
    const router = useRouter()

    const { data, isLoading, error } = useQuery({
        queryKey: ['session-bootstrap'],
        queryFn: async () => {
            const { data: sessionData } = await supabase.auth.getSession()

            if (!sessionData.session) {
                return { status: 'logged_out' as const }
            }

            const accessToken = sessionData.session.access_token

            const response = await api.get('/auth/session', {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            })

            return {
                status: 'authenticated' as const,
                appSession: response.data,
            }
        },
        retry: false,
    })

    useEffect(() => {
        if (!isLoading && data) {
            if (data.status === 'logged_out') {
                router.replace('/auth/login')
            }

            if (data.status === 'authenticated') {
                if (data.appSession.is_new_user) {
                    router.replace('/auth/onboarding')
                } else {
                    router.replace('/dashboard')
                }
            }
        }
    }, [data, isLoading, router])

    return {
        isLoading,
        error,
    }
}
