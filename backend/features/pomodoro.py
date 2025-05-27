"""Pomodoro Timer Feature Implementation"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class PomodoroState(Enum):
    """Enum representing the possible states of a Pomodoro timer."""
    IDLE = "idle"
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"


class PomodoroSession:
    """Represents a Pomodoro study session with configurable durations."""
    
    def __init__(self, 
                 name: str = "Study Session",
                 work_duration: int = 25,
                 short_break_duration: int = 5,
                 long_break_duration: int = 15,
                 long_break_interval: int = 4):
        self.name = name
        self.work_duration = work_duration  # minutes
        self.short_break_duration = short_break_duration  # minutes
        self.long_break_duration = long_break_duration  # minutes
        self.long_break_interval = long_break_interval  # number of work sessions before long break
        
        self.state = PomodoroState.IDLE
        self.current_cycle = 0
        self.completed_cycles = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.remaining_seconds: Optional[int] = None
        self.pause_time: Optional[datetime] = None
        self.paused_seconds = 0
        
        # Callbacks
        self.on_state_change: Optional[Callable[[PomodoroState], None]] = None
        self.on_timer_tick: Optional[Callable[[int], None]] = None
        self.on_cycle_complete: Optional[Callable[[int], None]] = None
        self.on_session_complete: Optional[Callable[[], None]] = None
        
        # Session statistics
        self.total_work_time = 0  # seconds
        self.total_break_time = 0  # seconds
        self.created_at = datetime.now()
    
    def start(self) -> None:
        """Start or resume the Pomodoro session."""
        if self.state == PomodoroState.IDLE:
            self.state = PomodoroState.WORK
            self.start_time = datetime.now()
            self.remaining_seconds = self.work_duration * 60
            self.current_cycle = 1
            
            if self.on_state_change:
                self.on_state_change(self.state)
        elif self.state == PomodoroState.PAUSED:
            # Calculate how long we were paused
            if self.pause_time:
                pause_duration = (datetime.now() - self.pause_time).total_seconds()
                self.paused_seconds += int(pause_duration)
            
            # Resume from paused state
            self.state = PomodoroState.WORK if self.remaining_seconds == self.work_duration * 60 else self.state
            self.pause_time = None
            
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def pause(self) -> None:
        """Pause the current Pomodoro session."""
        if self.state in [PomodoroState.WORK, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            self.pause_time = datetime.now()
            self.state = PomodoroState.PAUSED
            
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def stop(self) -> None:
        """Stop the current Pomodoro session."""
        if self.state != PomodoroState.IDLE:
            self.end_time = datetime.now()
            self.state = PomodoroState.IDLE
            self.remaining_seconds = None
            
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def skip(self) -> None:
        """Skip to the next phase of the Pomodoro session."""
        if self.state == PomodoroState.WORK:
            self._complete_work_cycle()
        elif self.state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            self._start_work_cycle()
    
    def reset(self) -> None:
        """Reset the Pomodoro session to its initial state."""
        self.state = PomodoroState.IDLE
        self.current_cycle = 0
        self.completed_cycles = 0
        self.start_time = None
        self.end_time = None
        self.remaining_seconds = None
        self.pause_time = None
        self.paused_seconds = 0
        self.total_work_time = 0
        self.total_break_time = 0
        
        if self.on_state_change:
            self.on_state_change(self.state)
    
    def tick(self) -> None:
        """Update the timer by one second."""
        if self.state in [PomodoroState.WORK, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK] and self.remaining_seconds is not None:
            self.remaining_seconds -= 1
            
            # Update statistics
            if self.state == PomodoroState.WORK:
                self.total_work_time += 1
            else:
                self.total_break_time += 1
            
            if self.on_timer_tick:
                self.on_timer_tick(self.remaining_seconds)
            
            # Check if the current phase is complete
            if self.remaining_seconds <= 0:
                if self.state == PomodoroState.WORK:
                    self._complete_work_cycle()
                else:  # SHORT_BREAK or LONG_BREAK
                    self._start_work_cycle()
    
    def _complete_work_cycle(self) -> None:
        """Complete a work cycle and transition to a break."""
        self.completed_cycles += 1
        
        if self.on_cycle_complete:
            self.on_cycle_complete(self.completed_cycles)
        
        # Determine if we need a short or long break
        if self.completed_cycles % self.long_break_interval == 0:
            self.state = PomodoroState.LONG_BREAK
            self.remaining_seconds = self.long_break_duration * 60
        else:
            self.state = PomodoroState.SHORT_BREAK
            self.remaining_seconds = self.short_break_duration * 60
        
        if self.on_state_change:
            self.on_state_change(self.state)
    
    def _start_work_cycle(self) -> None:
        """Start a new work cycle."""
        self.current_cycle += 1
        self.state = PomodoroState.WORK
        self.remaining_seconds = self.work_duration * 60
        
        if self.on_state_change:
            self.on_state_change(self.state)
    
    def get_formatted_time(self) -> str:
        """Get the remaining time formatted as MM:SS."""
        if self.remaining_seconds is None:
            return "00:00"
        
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_percentage(self) -> float:
        """Get the progress percentage of the current phase."""
        if self.state == PomodoroState.IDLE or self.remaining_seconds is None:
            return 0.0
        
        total_seconds = 0
        if self.state == PomodoroState.WORK:
            total_seconds = self.work_duration * 60
        elif self.state == PomodoroState.SHORT_BREAK:
            total_seconds = self.short_break_duration * 60
        elif self.state == PomodoroState.LONG_BREAK:
            total_seconds = self.long_break_duration * 60
        
        if total_seconds == 0:
            return 0.0
        
        return 100.0 * (1.0 - (self.remaining_seconds / total_seconds))
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session."""
        return {
            "name": self.name,
            "state": self.state.value,
            "current_cycle": self.current_cycle,
            "completed_cycles": self.completed_cycles,
            "total_work_time": self.total_work_time,
            "total_break_time": self.total_break_time,
            "remaining_time": self.get_formatted_time(),
            "progress": self.get_progress_percentage(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "work_duration": self.work_duration,
            "short_break_duration": self.short_break_duration,
            "long_break_duration": self.long_break_duration,
            "long_break_interval": self.long_break_interval,
            "state": self.state.value,
            "current_cycle": self.current_cycle,
            "completed_cycles": self.completed_cycles,
            "remaining_seconds": self.remaining_seconds,
            "paused_seconds": self.paused_seconds,
            "total_work_time": self.total_work_time,
            "total_break_time": self.total_break_time,
            "created_at": self.created_at.isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "pause_time": self.pause_time.isoformat() if self.pause_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PomodoroSession':
        """Create a PomodoroSession from a dictionary."""
        session = cls(
            name=data.get("name", "Study Session"),
            work_duration=data.get("work_duration", 25),
            short_break_duration=data.get("short_break_duration", 5),
            long_break_duration=data.get("long_break_duration", 15),
            long_break_interval=data.get("long_break_interval", 4)
        )
        
        session.state = PomodoroState(data.get("state", "idle"))
        session.current_cycle = data.get("current_cycle", 0)
        session.completed_cycles = data.get("completed_cycles", 0)
        session.remaining_seconds = data.get("remaining_seconds")
        session.paused_seconds = data.get("paused_seconds", 0)
        session.total_work_time = data.get("total_work_time", 0)
        session.total_break_time = data.get("total_break_time", 0)
        
        if data.get("created_at"):
            session.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("start_time"):
            session.start_time = datetime.fromisoformat(data["start_time"])
        
        if data.get("end_time"):
            session.end_time = datetime.fromisoformat(data["end_time"])
        
        if data.get("pause_time"):
            session.pause_time = datetime.fromisoformat(data["pause_time"])
        
        return session


class PomodoroManager:
    """Manages Pomodoro sessions and history."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "pomodoro"
        self.current_session: Optional[PomodoroSession] = None
        self.session_history: List[Dict[str, Any]] = []
        self.logger = get_logger("pomodoro")
        self.timer_task: Optional[asyncio.Task] = None
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Default session settings
        self.default_work_duration = 25
        self.default_short_break_duration = 5
        self.default_long_break_duration = 15
        self.default_long_break_interval = 4
    
    async def load_history(self) -> None:
        """Load session history from disk."""
        history_file = self.data_dir / "history.json"
        
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.session_history = json.load(f)
                self.logger.info(f"Loaded {len(self.session_history)} Pomodoro sessions from history")
            except Exception as e:
                self.logger.error(f"Error loading Pomodoro history: {e}")
    
    async def save_history(self) -> None:
        """Save session history to disk."""
        history_file = self.data_dir / "history.json"
        
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.session_history, f, indent=2)
            self.logger.info(f"Saved {len(self.session_history)} Pomodoro sessions to history")
        except Exception as e:
            self.logger.error(f"Error saving Pomodoro history: {e}")
    
    async def load_current_session(self) -> None:
        """Load the current session from disk if it exists."""
        session_file = self.data_dir / "current_session.json"
        
        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    self.current_session = PomodoroSession.from_dict(session_data)
                self.logger.info("Loaded current Pomodoro session")
            except Exception as e:
                self.logger.error(f"Error loading current Pomodoro session: {e}")
    
    async def save_current_session(self) -> None:
        """Save the current session to disk."""
        if not self.current_session:
            return
        
        session_file = self.data_dir / "current_session.json"
        
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
            self.logger.info("Saved current Pomodoro session")
        except Exception as e:
            self.logger.error(f"Error saving current Pomodoro session: {e}")
    
    def create_session(self, 
                       name: str = "Study Session",
                       work_duration: Optional[int] = None,
                       short_break_duration: Optional[int] = None,
                       long_break_duration: Optional[int] = None,
                       long_break_interval: Optional[int] = None) -> PomodoroSession:
        """Create a new Pomodoro session."""
        # Stop any existing session
        self.stop_session()
        
        # Use default values if not provided
        work_duration = work_duration or self.default_work_duration
        short_break_duration = short_break_duration or self.default_short_break_duration
        long_break_duration = long_break_duration or self.default_long_break_duration
        long_break_interval = long_break_interval or self.default_long_break_interval
        
        # Create new session
        self.current_session = PomodoroSession(
            name=name,
            work_duration=work_duration,
            short_break_duration=short_break_duration,
            long_break_duration=long_break_duration,
            long_break_interval=long_break_interval
        )
        
        # Set up callbacks
        self.current_session.on_state_change = self._on_state_change
        self.current_session.on_timer_tick = self._on_timer_tick
        self.current_session.on_cycle_complete = self._on_cycle_complete
        self.current_session.on_session_complete = self._on_session_complete
        
        self.logger.info(f"Created new Pomodoro session: {name}")
        return self.current_session
    
    def start_session(self) -> bool:
        """Start or resume the current Pomodoro session."""
        if not self.current_session:
            self.create_session()
        
        if self.current_session:
            self.current_session.start()
            
            # Start the timer task if not already running
            if not self.timer_task or self.timer_task.done():
                self.timer_task = asyncio.create_task(self._timer_loop())
            
            self.logger.info("Started Pomodoro session")
            return True
        
        return False
    
    def pause_session(self) -> bool:
        """Pause the current Pomodoro session."""
        if self.current_session:
            self.current_session.pause()
            self.logger.info("Paused Pomodoro session")
            return True
        
        return False
    
    def stop_session(self) -> bool:
        """Stop the current Pomodoro session and save to history."""
        if self.current_session:
            # Only save completed sessions to history
            if self.current_session.start_time:
                self.current_session.stop()
                self.session_history.append(self.current_session.to_dict())
                asyncio.create_task(self.save_history())
            
            # Cancel the timer task
            if self.timer_task and not self.timer_task.done():
                self.timer_task.cancel()
            
            self.current_session = None
            asyncio.create_task(self.save_current_session())
            
            self.logger.info("Stopped Pomodoro session")
            return True
        
        return False
    
    def skip_phase(self) -> bool:
        """Skip to the next phase of the current Pomodoro session."""
        if self.current_session:
            self.current_session.skip()
            self.logger.info("Skipped to next Pomodoro phase")
            return True
        
        return False
    
    def reset_session(self) -> bool:
        """Reset the current Pomodoro session."""
        if self.current_session:
            self.current_session.reset()
            self.logger.info("Reset Pomodoro session")
            return True
        
        return False
    
    def get_current_session(self) -> Optional[PomodoroSession]:
        """Get the current Pomodoro session."""
        return self.current_session
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session."""
        if self.current_session:
            return self.current_session.get_session_stats()
        
        return {
            "state": "idle",
            "current_cycle": 0,
            "completed_cycles": 0,
            "total_work_time": 0,
            "total_break_time": 0,
            "remaining_time": "00:00",
            "progress": 0.0
        }
    
    def get_history_stats(self) -> Dict[str, Any]:
        """Get statistics from session history."""
        if not self.session_history:
            return {
                "total_sessions": 0,
                "total_work_time": 0,
                "total_break_time": 0,
                "total_cycles": 0,
                "recent_sessions": []
            }
        
        total_work_time = sum(session.get("total_work_time", 0) for session in self.session_history)
        total_break_time = sum(session.get("total_break_time", 0) for session in self.session_history)
        total_cycles = sum(session.get("completed_cycles", 0) for session in self.session_history)
        
        # Get the 5 most recent sessions
        recent_sessions = sorted(
            self.session_history,
            key=lambda s: datetime.fromisoformat(s.get("created_at", "2000-01-01T00:00:00")),
            reverse=True
        )[:5]
        
        return {
            "total_sessions": len(self.session_history),
            "total_work_time": total_work_time,
            "total_break_time": total_break_time,
            "total_cycles": total_cycles,
            "recent_sessions": recent_sessions
        }
    
    def update_settings(self, 
                        work_duration: Optional[int] = None,
                        short_break_duration: Optional[int] = None,
                        long_break_duration: Optional[int] = None,
                        long_break_interval: Optional[int] = None) -> None:
        """Update the default session settings."""
        if work_duration is not None and work_duration > 0:
            self.default_work_duration = work_duration
        
        if short_break_duration is not None and short_break_duration > 0:
            self.default_short_break_duration = short_break_duration
        
        if long_break_duration is not None and long_break_duration > 0:
            self.default_long_break_duration = long_break_duration
        
        if long_break_interval is not None and long_break_interval > 0:
            self.default_long_break_interval = long_break_interval
        
        self.logger.info("Updated Pomodoro settings")
    
    async def _timer_loop(self) -> None:
        """Timer loop that ticks every second."""
        try:
            while self.current_session and self.current_session.state != PomodoroState.IDLE:
                if self.current_session.state != PomodoroState.PAUSED:
                    self.current_session.tick()
                    await self.save_current_session()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Pomodoro timer loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in Pomodoro timer loop: {e}")
    
    def _on_state_change(self, state: PomodoroState) -> None:
        """Callback for when the session state changes."""
        self.logger.info(f"Pomodoro state changed to: {state.value}")
        # This is where you would notify the UI or other components
    
    def _on_timer_tick(self, remaining_seconds: int) -> None:
        """Callback for each timer tick."""
        # This is where you would update the UI or other components
        pass
    
    def _on_cycle_complete(self, completed_cycles: int) -> None:
        """Callback for when a work cycle is completed."""
        self.logger.info(f"Completed Pomodoro cycle {completed_cycles}")
        # This is where you would notify the user or other components
    
    def _on_session_complete(self) -> None:
        """Callback for when the entire session is completed."""
        self.logger.info("Pomodoro session completed")
        # This is where you would notify the user or other components