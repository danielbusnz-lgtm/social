'use client'
import { useEffect, useState } from 'react'
import { Text, Strong } from '@/components/text'
import { Divider } from '@/components/divider'
import { apiFetch } from '@/lib/api'

type Post = {
    id: number
    content: string
    username: string
    created_at: string
    like_count: number
    liked_by_me: boolean
}

function timeAgo(iso: string) {
    const diffMs = Date.now() - new Date(iso).getTime()
    const sec = Math.floor(diffMs / 1000)
    if (sec < 60) return `${sec}s ago`
    const min = Math.floor(sec / 60)
    if (min < 60) return `${min}m ago`
    const hr = Math.floor(min / 60)
    if (hr < 24) return `${hr}h ago`
    const day = Math.floor(hr / 24)
    return `${day}d ago`
}

function LikeButton({
    post,
    onChange,
}: {
    post: Post
    onChange: (next: { like_count: number; liked_by_me: boolean }) => void
}) {
    const [pending, setPending] = useState(false)

    const handleClick = async () => {
        if (pending) return
        const previous = { like_count: post.like_count, liked_by_me: post.liked_by_me }
        const next = {
            like_count: post.like_count + (post.liked_by_me ? -1 : 1),
            liked_by_me: !post.liked_by_me,
        }
        onChange(next)
        setPending(true)
        try {
            const method = post.liked_by_me ? 'DELETE' : 'POST'
            const r = await apiFetch(`/posts/${post.id}/like`, { method })
            if (!r.ok) throw new Error(`like ${r.status}`)
        } catch {
            onChange(previous)
        } finally {
            setPending(false)
        }
    }

    return (
        <button
            type="button"
            onClick={handleClick}
            disabled={pending}
            aria-pressed={post.liked_by_me}
            className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 shadow-lg text-sm text-zinc-700 dark:text-white hover:bg-white/20 hover:text-red-500 disabled:opacity-50 transition"
        >
            <span>{post.liked_by_me ? '♥' : '♡'}</span>
            <span>{post.like_count}</span>
        </button>
    )
}

export function Feed({ refreshKey }: { refreshKey: number }) {
    const [posts, setPosts] = useState<Post[] | null>(null)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        apiFetch('/feed')
            .then((r) => {
                if (!r.ok) throw new Error(`${r.status}`)
                return r.json()
            })
            .then((data: Post[]) => setPosts(data))
            .catch((e) => setError(e.message))
    }, [refreshKey])

    const updatePost = (id: number, next: { like_count: number; liked_by_me: boolean }) => {
        setPosts((current) => current?.map((p) => (p.id === id ? { ...p, ...next } : p)) ?? null)
    }

    if (error) return <Text>Failed to load feed: {error}</Text>
    if (posts === null) return <Text>Loading…</Text>
    if (posts.length === 0) return <Text>No posts yet. Follow someone or write the first one.</Text>

    return (
        <div className="flex flex-col gap-4">
            {posts.map((post, i) => (
                <div key={post.id}>
                    {i > 0 && <Divider className="mb-4" />}
                    <div className="flex items-baseline gap-2">
                        <Strong>@{post.username}</Strong>
                        <Text className="text-xs">{timeAgo(post.created_at)}</Text>
                    </div>
                    <Text className="mt-1 whitespace-pre-wrap">{post.content}</Text>
                    <LikeButton post={post} onChange={(next) => updatePost(post.id, next)} />
                </div>
            ))}
        </div>
    )
}
