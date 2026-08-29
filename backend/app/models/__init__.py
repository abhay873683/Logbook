# ============================================================
# TreeFlow AI - SQLAlchemy Models Registry
# ============================================================

# Core User / Organization
from .user import User
from .company import Company
from .department import Department
from .team import Team

# Projects / Tasks
from .project import Project
from .project_user import ProjectUser
from .task import (
    Task,
    TaskStatusEnum,
    TaskPriorityEnum,
)
from .task_assignee import TaskAssignee
from .subtask import Subtask
from .dependency import Dependency

# Progress Tracking
from .task_progress import TaskProgress
from .subtask_progress import SubtaskProgress

# Comments
from .comment import Comment
from .comment_reply import CommentReply

# Files
from .file import File
from .file_share import FileShare
from .file_type import FileType
from .file_version import FileVersion
from .folder import Folder

# Notifications
from .notification import Notification
from .notification_preference import NotificationPreference
from .reminder import Reminder

# Activity / Event Logs
from .activity_log import ActivityLog
from .event_log import EventLog

# Reports
from .report import Report
from .report_schedule import ReportSchedule

# Day 41 - Time Tracking
from .time_log import TimeLog
from .timer_session import TimerSession
from .timesheet import Timesheet
from .timesheet_log import TimesheetLog

# Day 42 - Dashboard & Widgets
from .dashboard import Dashboard
from .widget import Widget

# Day 43 - Calendar & Events
from .event import Event
from .event_participant import EventParticipant
from .event_recurrence import EventRecurrence

# Day 46 - Leave & Attendance
from .leave import Leave
from .attendance import Attendance

# Chat / Messaging
from .chat import (
    Channel,
    ChannelMember,
    GroupChat,
    GroupMember,
    DirectMessage,
    Message,
)

# AI
from .ai import (
    AIChatSession,
    AIMessage,
    AISuggestion,
)