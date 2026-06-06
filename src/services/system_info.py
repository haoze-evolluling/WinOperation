import time
import psutil
from win32com.client import Dispatch


def _wmi():
    """Return a WMI service object connected to the local machine."""
    locator = Dispatch("WbemScripting.SWbemLocator")
    return locator.ConnectServer(".", "root/cimv2")


def get_boot_time_str():
    """Return boot time as 'yyyy-MM-dd HH:mm:ss' string, or 'N/A'."""
    try:
        from datetime import datetime
        return datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def get_uptime_str():
    """Return uptime as formatted Chinese string like '1 天 3 小时 15 分钟'."""
    try:
        total_sec = time.time() - psutil.boot_time()
        if total_sec <= 0:
            return "N/A"
        days = int(total_sec // 86400)
        hours = int((total_sec % 86400) // 3600)
        mins = int((total_sec % 3600) // 60)
        parts = []
        if days > 0:
            parts.append(f"{days} 天")
        if hours > 0:
            parts.append(f"{hours} 小时")
        parts.append(f"{mins} 分钟")
        return " ".join(parts)
    except Exception:
        return "N/A"


def get_cpu_name():
    """Return CPU name string from WMI, or 'N/A'."""
    try:
        wmi_svc = _wmi()
        for cpu in wmi_svc.ExecQuery("SELECT Name FROM Win32_Processor"):
            return cpu.Name.strip() if cpu.Name else "N/A"
    except Exception:
        pass
    return "N/A"


def get_cpu_cores():
    """Return list of dicts: [{'core_index': '0', 'load': 45}, ...]."""
    try:
        percents = psutil.cpu_percent(interval=0.5, percpu=True)
        return [
            {"core_index": str(i), "load": round(pct)}
            for i, pct in enumerate(percents)
        ]
    except Exception:
        pass
    return []


def get_cpu_frequency():
    """Return (current_mhz, max_mhz). Returns (0, 0) on failure."""
    try:
        freq = psutil.cpu_freq()
        return (round(freq.current), round(freq.max))
    except Exception:
        pass
    return (0, 0)


def get_cpu_usage():
    """Return CPU usage percentage as integer (0-100)."""
    try:
        return round(psutil.cpu_percent(interval=0.5))
    except Exception:
        pass
    return 0


def get_memory():
    """Return (total_gb, used_gb, available_gb, percent)."""
    try:
        mem = psutil.virtual_memory()
        total = round(mem.total / (1024 ** 3), 1)
        available = round(mem.available / (1024 ** 3), 1)
        used = round((mem.total - mem.available) / (1024 ** 3), 1)
        percent = round(mem.percent, 1)
        return (total, used, available, percent)
    except Exception:
        pass
    return (0.0, 0.0, 0.0, 0.0)


def get_swap():
    """Return (total_gb, used_gb, percent). Falls back to WMI on failure."""
    # Try psutil first
    try:
        swap = psutil.swap_memory()
        if swap.total > 0:
            total = round(swap.total / (1024 ** 3), 1)
            used = round(swap.used / (1024 ** 3), 1)
            percent = round(swap.percent, 1)
            return (total, used, percent)
    except Exception:
        pass

    # WMI fallback via Win32_PageFileUsage
    try:
        wmi_svc = _wmi()
        total_mb = 0
        used_mb = 0
        for pf in wmi_svc.ExecQuery(
            "SELECT AllocatedBaseSize, CurrentUsage FROM Win32_PageFileUsage"
        ):
            total_mb += int(pf.AllocatedBaseSize or 0)
            used_mb += int(pf.CurrentUsage or 0)
        if total_mb > 0:
            total = round(total_mb / 1024, 1)
            used = round(used_mb / 1024, 1)
            percent = round(used_mb / total_mb * 100, 1)
            return (total, used, percent)
    except Exception:
        pass

    return (0.0, 0.0, 0.0)


def get_disks():
    """Return list of disk dicts with device/total/free/used/percent."""
    disks = []
    try:
        for part in psutil.disk_partitions(all=False):
            if part.fstype == "" or "cdrom" in part.opts:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except (PermissionError, OSError):
                continue
            total = round(usage.total / (1024 ** 3), 1)
            free = round(usage.free / (1024 ** 3), 1)
            used = round(total - free, 1)
            percent = round((1 - free / total) * 100, 1) if total > 0 else 0
            disks.append({
                "device": part.device,
                "total": total,
                "free": free,
                "used": used,
                "percent": percent,
            })
    except Exception:
        pass
    return disks


def get_top_processes(n=5):
    """Return list of top-N CPU-consuming processes as dicts.

    Each dict: {'pid': int, 'name': str, 'cpu': float, 'memory_mb': float}
    """
    procs = []
    try:
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = p.info
                procs.append({
                    "pid": info["pid"],
                    "name": info["name"] or "",
                    "cpu": round(info["cpu_percent"] or 0.0, 1),
                    "memory_mb": round((info["memory_info"] or psutil._common.smem(0)).rss / (1024 * 1024), 1),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    procs.sort(key=lambda x: x["cpu"], reverse=True)
    return procs[:n]


def get_battery():
    """Return dict: {'present': bool, 'percentage': int, 'charging': bool}."""
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"present": False, "percentage": 0, "charging": False}
        return {
            "present": True,
            "percentage": round(bat.percent),
            "charging": bat.power_plugged,
        }
    except Exception:
        pass
    return {"present": False, "percentage": 0, "charging": False}
