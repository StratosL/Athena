/**
 * API client for backend communication.
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }))
    throw new Error(error.detail || error.error || `HTTP ${response.status}`)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

// Task types
export interface Task {
  id: string
  title: string
  description?: string
  quadrant: 1 | 2 | 3 | 4
  status: "pending" | "in_progress" | "completed"
  pomodoro_count: number
  due_date?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
}

export interface CreateTaskData {
  title: string
  description?: string
  quadrant: 1 | 2 | 3 | 4
  due_date?: string
}

export interface UpdateTaskData {
  title?: string
  description?: string
  quadrant?: 1 | 2 | 3 | 4
  status?: "pending" | "in_progress" | "completed"
  due_date?: string
}

// Daily Plan types
export interface TaskInfo {
  id: string
  title: string
  quadrant: 1 | 2 | 3 | 4
  status: "pending" | "in_progress" | "completed"
  pomodoro_count: number
}

export interface DailyPlan {
  id: string
  date: string
  major_task_id?: string
  medium_task_ids: string[]
  small_task_ids: string[]
  created_at: string
  updated_at: string
  completed: boolean
  completion_rate: number
  total_tasks: number
  completed_tasks: number
  major_task?: TaskInfo
  medium_tasks: TaskInfo[]
  small_tasks: TaskInfo[]
}

export interface DailyPlanListResponse {
  items: DailyPlan[]
  total: number
}

export type SlotType = "major" | "medium" | "small"

export interface TaskAssignment {
  task_id: string
  slot: SlotType
}

// Pomodoro types
export type TimerState = "IDLE" | "WORK" | "SHORT_BREAK" | "LONG_BREAK"

export interface PomodoroSession {
  id: string
  task_id: string | null
  started_at: string
  ended_at: string | null
  duration_minutes: number
  completed: boolean
  interrupted: boolean
  created_at: string
  updated_at: string
}

export interface ActiveTimer {
  session: PomodoroSession | null
  state: TimerState
  remaining_seconds: number
}

export interface PomodoroSessionListResponse {
  items: PomodoroSession[]
  total: number
}

// Task API functions
export const tasksApi = {
  list: (params?: { quadrant?: number; status?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.quadrant) searchParams.set("quadrant", String(params.quadrant))
    if (params?.status) searchParams.set("status", params.status)
    const query = searchParams.toString()
    return fetchApi<TaskListResponse>(`/tasks${query ? `?${query}` : ""}`)
  },

  get: (id: string) => fetchApi<Task>(`/tasks/${id}`),

  create: (data: CreateTaskData) =>
    fetchApi<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: UpdateTaskData) =>
    fetchApi<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    fetchApi<void>(`/tasks/${id}`, { method: "DELETE" }),

  complete: (id: string) =>
    fetchApi<Task>(`/tasks/${id}/complete`, { method: "POST" }),
}

// Daily Plan API functions
export const dailyPlansApi = {
  getToday: () => fetchApi<DailyPlan>("/daily-plans/today"),

  create: (date: string) =>
    fetchApi<DailyPlan>("/daily-plans", {
      method: "POST",
      body: JSON.stringify({ date }),
    }),

  get: (id: string) => fetchApi<DailyPlan>(`/daily-plans/${id}`),

  list: (params?: { limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set("limit", String(params.limit))
    if (params?.offset) searchParams.set("offset", String(params.offset))
    const query = searchParams.toString()
    return fetchApi<DailyPlanListResponse>(
      `/daily-plans${query ? `?${query}` : ""}`
    )
  },

  assignTask: (planId: string, assignment: TaskAssignment) =>
    fetchApi<DailyPlan>(`/daily-plans/${planId}/tasks`, {
      method: "POST",
      body: JSON.stringify(assignment),
    }),

  removeTask: (planId: string, taskId: string) =>
    fetchApi<DailyPlan>(`/daily-plans/${planId}/tasks/${taskId}`, {
      method: "DELETE",
    }),
}

// Pomodoro API functions
export const pomodoroApi = {
  getActive: () => fetchApi<ActiveTimer>("/pomodoro/active"),

  start: (taskId?: string) =>
    fetchApi<PomodoroSession>("/pomodoro/start", {
      method: "POST",
      body: JSON.stringify({ task_id: taskId }),
    }),

  stop: () =>
    fetchApi<PomodoroSession>("/pomodoro/stop", {
      method: "POST",
    }),

  complete: () =>
    fetchApi<PomodoroSession>("/pomodoro/complete", {
      method: "POST",
    }),

  listSessions: (taskId?: string, limit?: number) => {
    const params = new URLSearchParams()
    if (taskId) params.set("task_id", taskId)
    if (limit) params.set("limit", String(limit))
    const query = params.toString()
    return fetchApi<PomodoroSessionListResponse>(
      `/pomodoro/sessions${query ? `?${query}` : ""}`
    )
  },

  getSession: (id: string) => fetchApi<PomodoroSession>(`/pomodoro/sessions/${id}`),
}

// Analytics types
export type TimeRange = "day" | "week" | "month"

export interface PomodoroTrendPoint {
  date: string
  count: number
  total_minutes: number
}

export interface PomodoroTrendResponse {
  period: TimeRange
  data_points: PomodoroTrendPoint[]
  total_pomodoros: number
  total_minutes: number
  average_per_day: number
}

export interface TaskQuadrantStats {
  quadrant: number
  total: number
  completed: number
  completion_rate: number
}

export interface TaskDistributionResponse {
  quadrants: TaskQuadrantStats[]
  total_tasks: number
  total_completed: number
  overall_completion_rate: number
}

export interface DailyPlanStats {
  total_plans: number
  plans_completed: number
  average_completion_rate: number
  tasks_planned: number
  tasks_completed: number
}

export interface ProductivityScore {
  score: number
  components: Record<string, number>
  trend: "up" | "down" | "stable"
  trend_percentage: number
}

export interface AnalyticsSummary {
  period: TimeRange
  start_date: string
  end_date: string
  total_pomodoros: number
  total_focus_minutes: number
  average_pomodoros_per_day: number
  tasks_created: number
  tasks_completed: number
  task_completion_rate: number
  daily_plan_stats: DailyPlanStats
  productivity_score: ProductivityScore
}

// Analytics API functions
export const analyticsApi = {
  getSummary: (period: TimeRange = "week") =>
    fetchApi<AnalyticsSummary>(`/analytics/summary?period=${period}`),

  getPomodoroTrends: (period: TimeRange = "week") =>
    fetchApi<PomodoroTrendResponse>(`/analytics/pomodoro-trends?period=${period}`),

  getTaskDistribution: () =>
    fetchApi<TaskDistributionResponse>("/analytics/task-distribution"),
}
