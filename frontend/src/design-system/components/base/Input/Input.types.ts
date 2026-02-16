/**
 * Input Component Types
 * 
 * TypeScript interfaces for the glassmorphism Input component
 */

import * as React from "react"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    /** Error state */
    error?: boolean;
    /** Error message to display */
    errorMessage?: string;
    /** Additional CSS classes */
    className?: string;
}
