import * as React from "react"

export interface SwipeableTab {
  label: string
  content: React.ReactNode
}

export interface SwipeableTabsProps {
  tabs: SwipeableTab[]
  className?: string
}
