/**
 * TaskCard Component Types
 * 
 * TypeScript interfaces for the luxury task card
 */

import * as React from "react"

export interface TaskCardProps extends React.HTMLAttributes<HTMLDivElement> {
    /** Task ID for callbacks */
    id?: string;
    /** Task title */
    title: string;
    /** Task description */
    description?: string;
    /** Eisenhower quadrant (1-4) */
    quadrant: 1 | 2 | 3 | 4;
    /** Number of completed Pomodoros */
    pomodoroCount?: number;
    /** Whether task is completed */
    completed?: boolean;
    /** Callback when completion state changes */
    onCompletedChange?: (completed: boolean) => void;
    /** Callback when delete is clicked */
    onDelete?: (id: string) => void;
    /** Callback when card is clicked */
    onCardClick?: (id: string) => void;
    /** Additional CSS classes */
    className?: string;
}
