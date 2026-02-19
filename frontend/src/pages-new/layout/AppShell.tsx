import { useLocation } from "react-router-dom"
import { motion, AnimatePresence } from "motion/react"
import { MessageCircle } from "lucide-react"
import { PageHeader, Sidebar, BottomNav, ChatSidebar } from "@/design-system/components"
import type { PageHeaderProps } from "@/design-system/components"
import { useChatStore } from "@/stores/chatStore"
import { cn } from "@/lib/utils"
import { navItems, bottomNavItems } from "./navItems"

interface AppShellProps {
  title: string
  subtitle?: string
  actions?: PageHeaderProps["actions"]
  children: React.ReactNode
}

export function AppShell({ title, subtitle, actions, children }: AppShellProps) {
  const location = useLocation()
  const isOpen = useChatStore((s) => s.isOpen)
  const toggle = useChatStore((s) => s.toggle)
  const setOpen = useChatStore((s) => s.setOpen)
  const isAthenaPage = location.pathname === "/athena"

  const itemsWithActive = navItems.map((item) => ({
    ...item,
    active: location.pathname === item.href,
  }))

  const bottomItemsWithActive = bottomNavItems.map((item) => ({
    ...item,
    active: location.pathname === item.href,
  }))

  return (
    <div className="min-h-screen bg-luxury-obsidian">
      {/* Desktop Sidebar */}
      <Sidebar items={itemsWithActive} bottomItems={bottomItemsWithActive} className="hidden lg:flex fixed left-0 top-0 z-40" />

      {/* Mobile Bottom Nav */}
      <BottomNav items={itemsWithActive} />

      <div
        className={cn(
          "lg:pl-64 transition-[padding] duration-300",
          isOpen && !isAthenaPage && "lg:pr-[420px]"
        )}
      >
        <PageHeader title={title} subtitle={subtitle} actions={actions} />

        <main className="p-4 pb-20 lg:p-8 lg:pb-8">{children}</main>
      </div>

      {/* Athena Chat Sidebar + FAB (hidden on /athena page) */}
      {!isAthenaPage && (
        <>
          <ChatSidebar open={isOpen} onClose={() => setOpen(false)} />

          <AnimatePresence>
            {!isOpen && (
              <motion.button
                onClick={toggle}
                className={cn(
                  "fixed bottom-8 right-6 z-30 hidden lg:flex",
                  "w-14 h-14 rounded-full",
                  "bg-gradient-to-r from-luxury-accent to-luxury-gold",
                  "text-white shadow-lg shadow-luxury-accent/25",
                  "flex items-center justify-center"
                )}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                aria-label="Open Athena chat"
              >
                <MessageCircle size={24} />
              </motion.button>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  )
}
