/**
 * PageHeader Component Types
 * 
 * TypeScript interfaces for the glassmorphism page header
 */

import * as React from "react"

export interface PageHeaderProps extends React.HTMLAttributes<HTMLElement> {
    /** Page title */
    title: string;
    /** Optional subtitle */
    subtitle?: string;
    /** Action buttons to display on the right */
    actions?: React.ReactNode;
    /** Additional CSS classes */
    className?: string;
}
