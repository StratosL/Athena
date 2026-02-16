/**
 * Badge Component Types
 * 
 * TypeScript interfaces for quadrant indicator badges
 */

import * as React from "react"

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    /** Badge variant */
    variant?: 'q1' | 'q2' | 'q3' | 'q4' | 'gold' | 'default';
    /** Icon to display before text */
    icon?: React.ReactNode;
    /** Additional CSS classes */
    className?: string;
}
