/**
 * ProgressRing Component Types
 * 
 * TypeScript interfaces for the circular progress ring
 */

import * as React from "react"

export interface ProgressRingProps extends React.HTMLAttributes<HTMLDivElement> {
    /** Progress percentage (0-100) */
    percentage: number;
    /** Ring size in pixels */
    size?: number;
    /** Ring stroke width in pixels */
    strokeWidth?: number;
    /** Whether ring is in active state (pulsing glow) */
    active?: boolean;
    /** Content to display in center */
    children?: React.ReactNode;
    /** Additional CSS classes */
    className?: string;
}
