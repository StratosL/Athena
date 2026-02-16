/**
 * Shared TypeScript types for the Productivity App.
 */

// API Response types
export interface HealthResponse {
  status: string
  version: string
  database: string | null
}

export interface ErrorResponse {
  error: string
  code: string | null
  details: Record<string, unknown> | null
}

// Pagination types
export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// Task types (for Phase 2)
export type TaskQuadrant = 1 | 2 | 3 | 4
export type TaskStatus = "pending" | "in_progress" | "completed"

export interface Task {
  id: string
  title: string
  description?: string
  quadrant: TaskQuadrant
  status: TaskStatus
  pomodoroCount: number
  createdAt: string
  completedAt?: string
  dueDate?: string
}
