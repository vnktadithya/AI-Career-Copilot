// src/lib/types.ts

export type WritingTone =
  | 'formal'
  | 'casual'
  | 'technical'
  | 'storytelling'

export interface SamplePosts {
  linkedin?: string[]
  readme?: string[]
}

export interface UserPreferences {
  tone: WritingTone
  include_emojis: boolean
  sample_posts: SamplePosts
  portfolio_repo_url: string | null
  portfolio_branch: string | null
  auto_deploy: boolean
}

export interface ConnectedAccount {
  platform: 'github' | 'linkedin'
  connected: boolean
}
