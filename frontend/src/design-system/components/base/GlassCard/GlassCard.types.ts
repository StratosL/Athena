/**
 * GlassCard Component Types
 * 
 * TypeScript interfaces for the GlassCard glassmorphism container component
 */

import * as React from "react"

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    /** Enable hover lift effect */
    hoverable?: boolean;
    /** Additional CSS classes */
    className?: string;
    /** Child elements */
    children?: React.ReactNode;
}
