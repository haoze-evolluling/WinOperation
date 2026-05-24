import ctypes
from ctypes import wintypes

_advapi32 = ctypes.windll.advapi32

_InitiateSystemShutdownEx = _advapi32.InitiateSystemShutdownExW
_InitiateSystemShutdownEx.argtypes = [
    wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    wintypes.BOOL, wintypes.BOOL, wintypes.DWORD,
]
_InitiateSystemShutdownEx.restype = wintypes.BOOL

_AbortSystemShutdown = _advapi32.AbortSystemShutdownW
_AbortSystemShutdown.argtypes = [wintypes.LPCWSTR]
_AbortSystemShutdown.restype = wintypes.BOOL


def _enable_shutdown_privilege():
    """Enable SE_SHUTDOWN_NAME privilege for the current process.

    This is a best-effort operation — callers should proceed with the
    shutdown API regardless of whether this succeeds.
    """
    # Try pywin32 path first (works in most environments)
    try:
        import win32security
        import win32api
        try:
            h_token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
            )
            try:
                luid = win32security.LookupPrivilegeValue(None, "SeShutdownPrivilege")
                priv_state = [(luid, win32security.SE_PRIVILEGE_ENABLED)]
                win32security.AdjustTokenPrivileges(h_token, False, priv_state)
            finally:
                h_token.Close()
        except Exception:
            pass
    except ImportError:
        pass


def initiate_shutdown(timeout_seconds: int):
    """Schedule a system shutdown. Returns (success, message)."""
    _enable_shutdown_privilege()  # best-effort
    reason_code = 0x80000000
    try:
        ok = _InitiateSystemShutdownEx(
            None,
            "WinOperation 计划关机",
            timeout_seconds,
            True,
            False,
            reason_code,
        )
        if ok:
            return (True, f"已设置 {timeout_seconds} 秒后关机")
        err = ctypes.get_last_error()
        if err == 0:
            return (False, "设置关机定时器失败，请确认以管理员身份运行")
        return (False, f"设置关机定时器失败 (错误码: {err})")
    except Exception as e:
        return (False, f"设置关机定时器失败: {e}")


def abort_shutdown():
    """Cancel a pending system shutdown. Returns (success, message)."""
    try:
        ok = _AbortSystemShutdown(None)
        if ok:
            return (True, "已取消关机")
        err = ctypes.get_last_error()
        if err == 1116:
            return (True, "没有活动的关机任务")
        return (False, f"取消失败 (错误码: {err})")
    except Exception as e:
        return (False, f"取消失败: {e}")


TASK_FOLDER = "WinOperation"


def _get_scheduler():
    """Connect to the Task Scheduler COM service."""
    from win32com.client import Dispatch
    scheduler = Dispatch("Schedule.Service")
    scheduler.Connect()
    return scheduler


def _ensure_folder(root_folder):
    """Get or create the WinOperation task folder."""
    try:
        return root_folder.GetFolder(TASK_FOLDER)
    except Exception:
        return root_folder.CreateFolder(TASK_FOLDER)


def _day_bit(day_str: str) -> int:
    """Map day abbreviation to Task Scheduler day-of-week bitmask."""
    mapping = {
        "SUN": 1, "MON": 2, "TUE": 4, "WED": 8,
        "THU": 16, "FRI": 32, "SAT": 64,
    }
    return mapping.get(day_str.upper(), 0)


def create_scheduled_shutdown(days: list, time_str: str):
    """Create a weekly scheduled shutdown task.

    Args:
        days: list of weekday abbreviations, e.g. ['MON', 'TUE']
        time_str: 'HH:MM' format

    Returns (success, message).
    """
    try:
        scheduler = _get_scheduler()
        root_folder = scheduler.GetFolder("\\")
        folder = _ensure_folder(root_folder)

        hour, minute = time_str.split(":")
        task_name = f"ShutdownAt_{time_str.replace(':', '')}"

        task_def = scheduler.NewTask(0)

        trigger = task_def.Triggers.Create(3)  # TASK_TRIGGER_WEEKLY
        trigger.DaysOfWeek = sum(_day_bit(d) for d in days)
        trigger.StartBoundary = f"2000-01-01T{hour}:{minute}:00"

        action = task_def.Actions.Create(0)  # TASK_ACTION_EXEC
        action.Path = "shutdown.exe"
        action.Arguments = "/s /t 30"

        settings = task_def.Settings
        settings.Enabled = True
        settings.StartWhenAvailable = True
        settings.AllowDemandStart = True
        settings.Compatibility = 2  # TASK_COMPATIBILITY_V2_1

        folder.RegisterTaskDefinition(
            task_name, task_def, 6,  # TASK_CREATE_OR_UPDATE
            None, None, 0, None
        )

        return (True, f"已创建重复计划: {','.join(days)} {time_str}")
    except Exception as e:
        return (False, f"创建计划失败: {e}")


def list_scheduled_shutdowns():
    """Return list of task dicts from the WinOperation folder."""
    try:
        scheduler = _get_scheduler()
        root_folder = scheduler.GetFolder("\\")
        try:
            folder = root_folder.GetFolder(TASK_FOLDER)
        except Exception:
            return []

        tasks = []
        for task in folder.GetTasks(0):
            info = {"TaskName": task.Name, "State": str(task.State)}
            trigs = []
            for trig in task.Definition.Triggers:
                trigs.append({"Type": trig.Type, "StartBoundary": trig.StartBoundary})
            info["Triggers"] = trigs
            tasks.append(info)
        return tasks
    except Exception:
        return []


def delete_scheduled_shutdown(task_name: str):
    """Delete a task from the WinOperation folder by name. Returns (success, message)."""
    try:
        scheduler = _get_scheduler()
        root_folder = scheduler.GetFolder("\\")
        try:
            folder = root_folder.GetFolder(TASK_FOLDER)
        except Exception:
            return (False, "未找到 WinOperation 文件夹")

        folder.DeleteTask(task_name, 0)
        return (True, "计划已删除")
    except Exception as e:
        return (False, f"删除计划失败: {e}")
