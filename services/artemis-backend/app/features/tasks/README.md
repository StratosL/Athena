# Tasks Feature

Task management with Eisenhower Matrix prioritization.

## Overview

This feature provides CRUD operations for tasks, each assigned to one of four Eisenhower Matrix quadrants:

| Quadrant | Name | Action |
|----------|------|--------|
| 1 | Urgent + Important | Do First |
| 2 | Important, Not Urgent | Schedule |
| 3 | Urgent, Not Important | Delegate |
| 4 | Neither | Eliminate |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | List tasks (filterable by quadrant, status) |
| GET | `/tasks/{id}` | Get a single task |
| PATCH | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| POST | `/tasks/{id}/complete` | Mark task as completed |

## Database Schema

```sql
tasks (
  id UUID PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  quadrant INTEGER NOT NULL (1-4),
  status VARCHAR(20) DEFAULT 'pending',
  pomodoro_count INTEGER DEFAULT 0,
  due_date DATE,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
)
```

## Logging Events

- `task.create_started` / `task.create_completed` / `task.create_failed`
- `task.get_started` / `task.get_completed` / `task.get_failed`
- `task.list_started` / `task.list_completed` / `task.list_failed`
- `task.update_started` / `task.update_completed` / `task.update_failed`
- `task.delete_started` / `task.delete_completed` / `task.delete_failed`
- `task.complete_started` / `task.complete_completed` / `task.complete_failed`
