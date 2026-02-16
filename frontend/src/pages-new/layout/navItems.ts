import {
  Home,
  CheckSquare,
  Calendar,
  Timer,
  BarChart3,
  BookOpen,
  Settings,
} from "lucide-react"
import { createElement } from "react"
import type { SidebarNavItem } from "@/design-system/components"

export const navItems: SidebarNavItem[] = [
  { label: "Dashboard", href: "/", icon: createElement(Home, { className: "w-5 h-5" }) },
  { label: "Tasks", href: "/tasks", icon: createElement(CheckSquare, { className: "w-5 h-5" }) },
  { label: "Daily Plan", href: "/daily-plan", icon: createElement(Calendar, { className: "w-5 h-5" }) },
  { label: "Pomodoro", href: "/pomodoro", icon: createElement(Timer, { className: "w-5 h-5" }) },
  { label: "Analytics", href: "/analytics", icon: createElement(BarChart3, { className: "w-5 h-5" }) },
]

export const bottomNavItems: SidebarNavItem[] = [
  { label: "Guide", href: "/guide", icon: createElement(BookOpen, { className: "w-5 h-5" }) },
  { label: "Settings", href: "/settings", icon: createElement(Settings, { className: "w-5 h-5" }) },
]
