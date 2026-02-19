import { X, Plus, Trash2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

interface ConversationListProps {
  onSelect: () => void
  showCloseButton?: boolean
}

export function ConversationList({ onSelect, showCloseButton = true }: ConversationListProps) {
  const conversations = useChatStore((s) => s.conversations)
  const conversationId = useChatStore((s) => s.conversationId)
  const switchConversation = useChatStore((s) => s.switchConversation)
  const deleteConversation = useChatStore((s) => s.deleteConversation)
  const newConversation = useChatStore((s) => s.newConversation)

  const handleSwitch = (id: string) => {
    switchConversation(id)
    onSelect()
  }

  const handleNew = () => {
    newConversation()
    onSelect()
  }

  const sorted = [...conversations].sort((a, b) => b.updatedAt - a.updatedAt)

  return (
    <div className="flex flex-col h-full">
      <div className="px-1 pb-3 flex items-center justify-between">
        <span className="text-luxury-text-secondary text-xs font-medium uppercase tracking-wider">
          History
        </span>
        {showCloseButton && (
          <button
            onClick={onSelect}
            className="p-1 rounded-md text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
            aria-label="Close history"
          >
            <X size={14} />
          </button>
        )}
      </div>

      <button
        onClick={handleNew}
        className="w-full flex items-center gap-2 px-3 py-2.5 mb-2 rounded-lg border border-dashed border-luxury-border text-luxury-text-secondary hover:border-luxury-indigo hover:text-luxury-indigo text-sm transition-colors"
      >
        <Plus size={14} />
        New conversation
      </button>

      <div className="flex-1 overflow-y-auto space-y-1">
        {sorted.length === 0 ? (
          <p className="text-luxury-text-secondary text-xs text-center py-8">
            No conversations yet
          </p>
        ) : (
          sorted.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                "group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors",
                conv.id === conversationId
                  ? "bg-luxury-indigo/10 border border-luxury-indigo/30"
                  : "hover:bg-luxury-card border border-transparent"
              )}
              onClick={() => handleSwitch(conv.id)}
            >
              <div className="flex-1 min-w-0">
                <p className="text-luxury-text-primary text-sm truncate">
                  {conv.title}
                </p>
                <p className="text-luxury-text-secondary text-xs">
                  {new Date(conv.updatedAt).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  deleteConversation(conv.id)
                }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-luxury-text-secondary hover:text-red-400 transition-all"
                aria-label="Delete conversation"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
