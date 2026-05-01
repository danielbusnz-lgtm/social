'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export function AuthGate({ children }: { children: React.ReactNode }) {
    const router = useRouter()
    const [ready, setReady] = useState(false)

    useEffect(() => {
        const token = localStorage.getItem('token')
        if (!token) {
            router.replace('/login')
        } else {
            // eslint-disable-next-line react-hooks/set-state-in-effect -- localStorage is only available client-side
            setReady(true)
        }
    }, [router])

    if (!ready) return null
    return <>{children}</>
}
