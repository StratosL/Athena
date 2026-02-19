import { ConversationList } from "@/design-system/components/features/ChatSidebar/shared"

export function ConversationPanel() {
  return (
    <div className="w-72 hidden lg:flex flex-col backdrop-blur-md bg-luxury-card/50 border border-luxury-border rounded-xl p-4">
      <ConversationList onSelect={() => {}} showCloseButton={false} />
    </div>
  )
}
