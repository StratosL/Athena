/**
 * Button Component Types
 * 
 * TypeScript interfaces for the luxury Button component
 */

import * as React from "react"

// This will be imported from the component file
export interface ButtonVariants {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
}

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    /** Button variant */
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    /** Button size */
    size?: 'sm' | 'md' | 'lg';
    /** Loading state */
    loading?: boolean;
    /** Icon to display before text */
    icon?: React.ReactNode;
    /** Additional CSS classes */
    className?: string;
}
