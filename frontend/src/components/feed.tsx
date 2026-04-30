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
            className="group mt-2 inline-flex items-center gap-2 text-sm text-zinc-500 disabled:opacity-50"
        >
            {post.liked_by_me ? (
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="size-5 fill-white/30 drop-shadow-[0_0_4px_rgba(255,255,255,0.8)] group-hover:fill-red-500/60 group-hover:drop-shadow-[0_0_6px_rgba(239,68,68,0.8)] transition">
                    <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 0 1-.383-.218 25.18 25.18 0 0 1-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.514 3 7.5 3a5.5 5.5 0 0 1 4.5 2.3A5.5 5.5 0 0 1 16.5 3c2.986 0 5.25 2.322 5.25 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 0 1-4.244 3.17 15.247 15.247 0 0 1-.383.219l-.022.012-.007.004-.003.001a.752.752 0 0 1-.704 0l-.003-.001Z" />
                </svg>
            ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-5 stroke-white/60 drop-shadow-[0_0_4px_rgba(255,255,255,0.8)] group-hover:stroke-red-500 transition">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
                </svg>
            )}
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
