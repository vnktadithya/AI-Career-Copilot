import axios from 'axios'
import { supabase } from '@/lib/supabaseClient'

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
})

// 🔑 Attach Supabase access token to every request
api.interceptors.request.use(
  async (config) => {
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)
