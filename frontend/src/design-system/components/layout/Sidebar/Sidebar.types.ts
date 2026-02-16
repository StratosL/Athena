/**
 * Sidebar Component Types
 * 
 * TypeScript interfaces for the navigation sidebar
 */

import * as React from "react"

export interface SidebarNavItem {
    /** Navigation item label */
    label: string;
    /** Navigation item icon */
    icon: React.ReactNode;
    /** Navigation item href */
    href: string;
    /** Whether this item is active */
    active?: boolean;
}

export interface SidebarProps extends React.HTMLAttributes<HTMLElement> {
    /** Navigation items */
    items: SidebarNavItem[];
    /** Items pinned to the bottom of the sidebar (e.g. Settings, Guide) */
    bottomItems?: SidebarNavItem[];
    /** Whether sidebar is collapsed */
    collapsed?: boolean;
    /** Callback when collapse state changes */
    onCollapsedChange?: (collapsed: boolean) => void;
    /** Additional CSS classes */
    className?: string;
}
