import { ApplicationLayout } from '@/app/application-layout'
import { AuthGate } from '@/components/auth-gate'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <ApplicationLayout>{children}</ApplicationLayout>
    </AuthGate>
  )
}
