'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useQuery, useMutation } from '@tanstack/react-query'
import { supabase } from '@/lib/supabaseClient'

type Tone = 'formal' | 'casual' | 'technical' | 'storytelling'

type SamplePosts = {
  linkedin?: string[]
  readme?: string[]
}

type UserPreferences = {
  tone: Tone
  include_emojis: boolean
  sample_posts: SamplePosts
  portfolio_repo_url: string | null
  portfolio_branch: string | null
  auto_deploy: boolean
}

// helper function for github
const handleConnectGitHub = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const userId = session?.user.id

  if (!userId) {
    alert('User not authenticated')
    return
  }

  window.location.href =
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/users/me/connect/github?state=${userId}`
}

// helper function for linkedin
const handleConnectLinkedIn = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const accessToken = session?.access_token

  if (!accessToken) {
    alert('User not authenticated')
    return
  }

  window.location.href =
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/users/me/connect/linkedin?access_token=${accessToken}`
}


export default function SettingsPage() {
  const [form, setForm] = useState<UserPreferences | null>(null)
  const [sampleType, setSampleType] = useState<'linkedin' | 'readme'>('linkedin')

  // Fetch preferences
  const {
  data,
  isLoading,
  error,
} = useQuery({
  queryKey: ['user-preferences'],
  queryFn: async () => {
    const res = await api.get('/api/v1/users/me/preferences')

  if (!res.data.exists) {
    // New user → return defaults
    return {
      tone: 'storytelling',
      include_emojis: true,
      sample_posts: {},
      portfolio_repo_url: null,
      portfolio_branch: null,
      auto_deploy: false,
    }
  }

  // Existing user
  return res.data.preferences

  },
})


  // Save preferences
  const saveMutation = useMutation({
    mutationFn: async (payload: UserPreferences) => {
      await api.post('/api/v1/users/me/preferences', payload)
    },
  })

  useEffect(() => {
    if (data) {
      setForm({
        tone: data.tone,
        include_emojis: data.include_emojis,
        sample_posts: data.sample_posts ?? {},
        portfolio_repo_url: data.portfolio_repo_url ?? null,
        portfolio_branch: data.portfolio_branch ?? null,
        auto_deploy: data.auto_deploy ?? false,
      })
    }
  }, [data])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <p className="text-sm text-zinc-400">Loading preferences…</p>
      </div>
    )
  }

  if (error) {
    console.error('Preferences API error:', error)

    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <p className="text-sm text-red-400">
          Failed to load preferences
        </p>
      </div>
    )
  }

  if (!form) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <p className="text-sm text-zinc-400">
          Initializing preferences…
        </p>
      </div>
    )
  }

  const samples = form.sample_posts[sampleType] ?? []

  return (
    <div className="min-h-screen bg-black text-white px-6 py-12">
      <div className="max-w-3xl mx-auto space-y-10">

        <h1 className="text-2xl font-semibold tracking-tight">
          Preferences
        </h1>

        {/* Writing Style */}
        <section className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6 space-y-4">
          <h2 className="font-medium">Writing Style</h2>

          <select
            className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
            value={form.tone}
            onChange={(e) =>
              setForm({ ...form, tone: e.target.value as Tone })
            }
          >
            <option value="formal">Formal</option>
            <option value="casual">Casual</option>
            <option value="technical">Technical</option>
            <option value="storytelling">Storytelling</option>
          </select>

          <label className="flex items-center justify-between text-sm">
            <span>Include emojis in generated content</span>
            <input
              type="checkbox"
              checked={form.include_emojis}
              onChange={(e) =>
                setForm({ ...form, include_emojis: e.target.checked })
              }
            />
          </label>
        </section>

        {/* Sample Posts */}
        <section className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="font-medium">Sample Posts</h2>

            <select
              className="rounded-xl bg-black/40 border border-white/10 px-3 py-2 text-sm"
              value={sampleType}
              onChange={(e) =>
                setSampleType(e.target.value as 'linkedin' | 'readme')
              }
            >
              <option value="linkedin">LinkedIn</option>
              <option value="readme">README</option>
            </select>
          </div>

          {samples.map((text, idx) => (
            <textarea
              key={idx}
              className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-3 text-sm"
              placeholder={`Sample ${idx + 1}`}
              value={text}
              onChange={(e) => {
                const next = [...samples]
                next[idx] = e.target.value
                setForm({
                  ...form,
                  sample_posts: {
                    ...form.sample_posts,
                    [sampleType]: next,
                  },
                })
              }}
            />
          ))}

          <button
            className="text-sm text-indigo-400 hover:underline"
            onClick={() => {
              setForm({
                ...form,
                sample_posts: {
                  ...form.sample_posts,
                  [sampleType]: [...samples, ''],
                },
              })
            }}
          >
            + Add sample
          </button>
        </section>

        {/* Portfolio */}
        <section className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6 space-y-4">
          <h2 className="font-medium">Portfolio</h2>

          <input
            className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
            placeholder="Portfolio repository URL"
            value={form.portfolio_repo_url ?? ''}
            onChange={(e) =>
              setForm({
                ...form,
                portfolio_repo_url: e.target.value || null,
              })
            }
          />

          <input
            className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-2.5 text-sm"
            placeholder="Portfolio branch"
            value={form.portfolio_branch ?? ''}
            onChange={(e) =>
              setForm({
                ...form,
                portfolio_branch: e.target.value || null,
              })
            }
          />

          <label className="flex items-center justify-between text-sm">
            <span>Auto deploy after approved changes</span>
            <input
              type="checkbox"
              checked={form.auto_deploy}
              onChange={(e) =>
                setForm({ ...form, auto_deploy: e.target.checked })
              }
            />
          </label>
        </section>

        {/* Connect Platforms */}
        <section className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6 space-y-3">
          <h2 className="font-medium">Connected Platforms</h2>
          <button
            onClick={handleConnectGitHub}
            className="w-full rounded-xl border border-white/10 py-2.5 text-sm hover:bg-white/5 transition"
          >
            Connect GitHub
          </button>

          <button
            onClick={handleConnectLinkedIn}
            className="w-full rounded-xl border border-white/10 py-2.5 text-sm hover:bg-white/5 transition"
          >
            Connect LinkedIn
          </button>
        </section>

        {/* Save */}
        <button
          disabled={saveMutation.isPending}
          onClick={() => saveMutation.mutate(form)}
          className="w-full rounded-xl bg-white text-black py-3 text-sm font-medium hover:opacity-90 transition disabled:opacity-50"
        >
          Save Preferences
        </button>

      </div>
    </div>
  )
}
