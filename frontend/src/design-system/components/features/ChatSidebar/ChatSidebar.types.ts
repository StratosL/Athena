/**
 * ChatSidebar Component Types
 *
 * TypeScript interfaces for the Athena chat sidebar
 */

export interface ChatSidebarProps {
  /** Whether the sidebar is open */
  open: boolean
  /** Callback when sidebar should close */
  onClose: () => void
}
