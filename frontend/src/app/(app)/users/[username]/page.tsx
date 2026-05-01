'use client'
import { apiFetch } from '@/lib/api'
import { use, useEffect, useState } from 'react'
import { Heading, Subheading } from '@/components/heading'
import { Text, Strong } from '@/components/text'
import { Divider } from '@/components/divider'
import { FollowButton } from '@/components/follow-button'

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

type User = {
    id: number
    username: string
    created_at: string
    post_count: number
    follower_count: number
    following_count: number
    is_followed_by_me: boolean
}

type Post = {
    id: number
    content: string
    username: string
    created_at: string
    like_count: number
    liked_by_me: boolean
}

export default function UserProfilePage({ params }: { params: Promise<{ username: string }> }) {
    const { username } = use(params)
    const [user, setUser] = useState<User | null>(null)
    const [posts, setPosts] = useState<Post[] | null>(null)

    useEffect(() => {
        apiFetch(`/users/${username}`)
            .then((r) => r.json())
            .then((data) => setUser(data))

        apiFetch(`/users/${username}/posts`)
            .then((r) => r.json())
            .then((data) => setPosts(data))
    }, [username])

    if (user === null || posts === null) return <div>Loading…</div>

    const joined = new Date(user.created_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
    })

    return (
        <div className="mx-auto flex w-full max-w-xl flex-col gap-8 p-8">
            <div>
                <div className="flex items-center justify-between gap-4">
                    <Heading>@{user.username}</Heading>
                    <FollowButton
                        userId={user.id}
                        isFollowing={user.is_followed_by_me}
                        onChange={(next) => setUser({ ...user, is_followed_by_me: next })}
                    />
                </div>
                <Text className="mt-1">
                    Joined {joined} · {user.post_count} post
                    {user.post_count === 1 ? '' : 's'}
                </Text>
            </div>

            <Divider />

            <div>
                <Subheading>Posts</Subheading>
                {posts.length === 0 ? (
                    <Text className="mt-4">@{user.username} hasn&apos;t posted yet.</Text>
                ) : (
                    <div className="mt-4 flex flex-col gap-4">
                        {posts.map((post, i) => (
                            <div key={post.id}>
                                {i > 0 && <Divider className="mb-4" />}
                                <div className="flex items-baseline gap-2">
                                    <Strong>@{post.username}</Strong>
                                    <Text className="text-xs">{timeAgo(post.created_at)}</Text>
                                </div>
                                <Text className="mt-1 whitespace-pre-wrap">{post.content}</Text>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
