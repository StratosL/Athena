"""Tests for atomic pomodoro count increment."""

from unittest.mock import MagicMock, Mock

import pytest

from app.features.pomodoro.repository import PomodoroRepository
from app.features.tasks.exceptions import TaskNotFoundError


class TestAtomicIncrement:
    """Test atomic increment functionality."""

    def test_increment_task_pomodoro_count_success(self) -> None:
        """Test successful atomic increment."""
        # Arrange
        mock_db = MagicMock()
        mock_result = Mock()
        mock_result.data = 3  # New count after increment
        mock_db.rpc.return_value.execute.return_value = mock_result

        repo = PomodoroRepository(mock_db)
        task_id = "550e8400-e29b-41d4-a716-446655440000"

        # Act
        repo.increment_task_pomodoro_count(task_id)

        # Assert - verify RPC call with correct parameters
        mock_db.rpc.assert_called_once_with("increment_pomodoro_count", {"p_task_id": task_id})
        mock_db.rpc.return_value.execute.assert_called_once()

    def test_increment_task_pomodoro_count_task_not_found(self) -> None:
        """Test increment raises TaskNotFoundError when task doesn't exist."""
        # Arrange
        mock_db = MagicMock()
        mock_result = Mock()
        mock_result.data = None  # NULL returned when task doesn't exist
        mock_db.rpc.return_value.execute.return_value = mock_result

        repo = PomodoroRepository(mock_db)
        task_id = "nonexistent-task-id"

        # Act & Assert
        with pytest.raises(TaskNotFoundError) as exc_info:
            repo.increment_task_pomodoro_count(task_id)

        assert "Task 'nonexistent-task-id' not found" in str(exc_info.value)

    def test_increment_task_pomodoro_count_database_error(self) -> None:
        """Test increment handles database errors correctly."""
        # Arrange
        mock_db = MagicMock()
        mock_db.rpc.return_value.execute.side_effect = Exception("Database connection lost")

        repo = PomodoroRepository(mock_db)
        task_id = "550e8400-e29b-41d4-a716-446655440000"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            repo.increment_task_pomodoro_count(task_id)

        assert "Database connection lost" in str(exc_info.value)

    def test_increment_is_atomic_single_rpc_call(self) -> None:
        """Test that increment uses single RPC call (no read-modify-write)."""
        # Arrange
        mock_db = MagicMock()
        mock_result = Mock()
        mock_result.data = 1
        mock_db.rpc.return_value.execute.return_value = mock_result

        repo = PomodoroRepository(mock_db)
        task_id = "550e8400-e29b-41d4-a716-446655440000"

        # Act
        repo.increment_task_pomodoro_count(task_id)

        # Assert - only ONE RPC call, no SELECT + UPDATE pattern
        assert mock_db.rpc.call_count == 1
        # Ensure no table() calls (would indicate read-modify-write)
        mock_db.table.assert_not_called()
