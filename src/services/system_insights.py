import os
import platform
import socket
import sys
import time

import psutil

from services.network_mgmt import get_network_status
from services.system_info import (
    get_battery,
    get_boot_time_str,
    get_cpu_cores,
    get_cpu_frequency,
    get_cpu_usage,
    get_disks,
    get_memory,
    get_swap,
    get_top_processes,
    get_uptime_str,
)


FEATURE_IDS = [
    "health_score",
    "risk_alerts",
    "system_profile",
    "uptime_analysis",
    "cpu_load",
    "cpu_core_heatmap",
    "memory_pressure",
    "swap_pressure",
    "disk_summary",
    "disk_low_space",
    "storage_io",
    "network_throughput",
    "network_errors",
    "active_connections",
    "interface_inventory",
    "dns_snapshot",
    "top_cpu_processes",
    "top_memory_processes",
    "service_summary",
    "battery_runtime",
]


def _pct(value):
    try:
        return round(float(value), 1)
    except Exception:
        return 0.0


def _severity_by_percent(value, warning=75, critical=90):
    value = _pct(value)
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "ok"


def _severity_label(severity):
    return {
        "ok": "正常",
        "info": "信息",
        "warning": "关注",
        "critical": "紧急",
    }.get(severity, "信息")


def _feature(feature_id, title, value, detail, severity="ok", metrics=None, actions=None):
    return {
        "id": feature_id,
        "title": title,
        "value": str(value),
        "detail": detail,
        "severity": severity,
        "status_label": _severity_label(severity),
        "metrics": metrics or {},
        "actions": actions or [],
    }


def _gb(value):
    try:
        return f"{round(float(value), 1)} GB"
    except Exception:
        return "0 GB"


def _days_from_seconds(seconds):
    try:
        return round(float(seconds) / 86400, 1)
    except Exception:
        return 0.0


def _recommend(recommendations, message):
    if message and message not in recommendations:
        recommendations.append(message)


def _format_processes(processes):
    rows = []
    for proc in processes[:5]:
        rows.append({
            "pid": proc.get("pid", 0),
            "name": proc.get("name", ""),
            "cpu": _pct(proc.get("cpu", 0)),
            "memory_mb": _pct(proc.get("memory_mb", 0)),
        })
    return rows


def _top_memory_processes(limit=5):
    rows = []
    try:
        attrs = ["pid", "name", "memory_info", "cpu_percent"]
        for proc in psutil.process_iter(attrs):
            try:
                info = proc.info
                mem = info.get("memory_info")
                rows.append({
                    "pid": info.get("pid", 0),
                    "name": info.get("name") or "",
                    "cpu": round(info.get("cpu_percent") or 0, 1),
                    "memory_mb": round((mem.rss if mem else 0) / (1024 * 1024), 1),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        return []
    rows.sort(key=lambda item: item["memory_mb"], reverse=True)
    return rows[:limit]


def _service_summary():
    if not hasattr(psutil, "win_service_iter"):
        return {"supported": False, "total": 0, "running": 0, "stopped": 0, "paused": 0}

    summary = {"supported": True, "total": 0, "running": 0, "stopped": 0, "paused": 0}
    try:
        for service in psutil.win_service_iter():
            try:
                status = service.status()
            except Exception:
                status = ""
            summary["total"] += 1
            if status == "running":
                summary["running"] += 1
            elif status == "paused":
                summary["paused"] += 1
            elif status:
                summary["stopped"] += 1
    except Exception:
        summary["supported"] = False
    return summary


def _connection_summary():
    summary = {"total": 0, "listening": 0, "established": 0}
    try:
        for conn in psutil.net_connections(kind="inet"):
            summary["total"] += 1
            status = (conn.status or "").upper()
            if status == "LISTEN":
                summary["listening"] += 1
            elif status == "ESTABLISHED":
                summary["established"] += 1
    except Exception:
        pass
    return summary


def _disk_io_summary():
    try:
        counters = psutil.disk_io_counters()
        if not counters:
            return {"read_mb": 0, "write_mb": 0, "read_count": 0, "write_count": 0}
        return {
            "read_mb": round(counters.read_bytes / (1024 * 1024), 1),
            "write_mb": round(counters.write_bytes / (1024 * 1024), 1),
            "read_count": counters.read_count,
            "write_count": counters.write_count,
        }
    except Exception:
        return {"read_mb": 0, "write_mb": 0, "read_count": 0, "write_count": 0}


def _net_io_summary():
    try:
        counters = psutil.net_io_counters()
        if not counters:
            raise RuntimeError("net io counters unavailable")
        return {
            "bytes_sent_mb": round(counters.bytes_sent / (1024 * 1024), 1),
            "bytes_recv_mb": round(counters.bytes_recv / (1024 * 1024), 1),
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
            "errin": counters.errin,
            "errout": counters.errout,
            "dropin": counters.dropin,
            "dropout": counters.dropout,
        }
    except Exception:
        return {
            "bytes_sent_mb": 0,
            "bytes_recv_mb": 0,
            "packets_sent": 0,
            "packets_recv": 0,
            "errin": 0,
            "errout": 0,
            "dropin": 0,
            "dropout": 0,
        }


def _battery_with_runtime():
    data = get_battery()
    try:
        bat = psutil.sensors_battery()
        data["secsleft"] = getattr(bat, "secsleft", None) if bat else None
    except Exception:
        data["secsleft"] = None
    return data


def _is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def collect_insight_raw():
    ram_total, ram_used, ram_available, ram_percent = get_memory()
    swap_total, swap_used, swap_percent = get_swap()
    current_freq, max_freq = get_cpu_frequency()

    try:
        adapters, connections = get_network_status()
    except Exception:
        adapters, connections = [], []

    try:
        uptime_seconds = max(0, time.time() - psutil.boot_time())
    except Exception:
        uptime_seconds = 0

    return {
        "system": {
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "hostname": platform.node() or socket.gethostname(),
            "architecture": os.environ.get("PROCESSOR_ARCHITECTURE", platform.machine()),
            "login_user": os.environ.get("USERNAME") or os.environ.get("USER") or "",
            "uptime": get_uptime_str(),
            "uptime_seconds": uptime_seconds,
            "boot_time": get_boot_time_str(),
            "admin": _is_admin(),
            "python_version": platform.python_version(),
            "executable": os.path.basename(sys.executable),
        },
        "cpu": {
            "usage": get_cpu_usage(),
            "physical_cores": psutil.cpu_count(logical=False) or 0,
            "logical_cores": psutil.cpu_count(logical=True) or 0,
            "frequency_current": current_freq,
            "frequency_max": max_freq,
            "cores": get_cpu_cores(),
        },
        "memory": {
            "total_gb": ram_total,
            "used_gb": ram_used,
            "available_gb": ram_available,
            "percent": ram_percent,
        },
        "swap": {"total_gb": swap_total, "used_gb": swap_used, "percent": swap_percent},
        "disks": get_disks(),
        "disk_io": _disk_io_summary(),
        "network": {"adapters": adapters, "connections": connections},
        "net_io": _net_io_summary(),
        "connections": _connection_summary(),
        "processes": get_top_processes(8),
        "memory_processes": _top_memory_processes(8),
        "services": _service_summary(),
        "battery": _battery_with_runtime(),
    }


def compose_insights(raw):
    recommendations = []
    health_score = 100

    cpu = raw.get("cpu", {})
    memory = raw.get("memory", {})
    swap = raw.get("swap", {})
    disks = raw.get("disks", [])
    net_io = raw.get("net_io", {})
    connections = raw.get("connections", {})
    network = raw.get("network", {})
    services = raw.get("services", {})
    battery = raw.get("battery", {})
    system = raw.get("system", {})

    cpu_usage = _pct(cpu.get("usage", 0))
    mem_percent = _pct(memory.get("percent", 0))
    swap_percent = _pct(swap.get("percent", 0))
    uptime_days = _days_from_seconds(system.get("uptime_seconds", 0))
    low_disks = [disk for disk in disks if _pct(disk.get("percent", 0)) >= 90]
    warn_disks = [disk for disk in disks if 80 <= _pct(disk.get("percent", 0)) < 90]
    net_errors = sum(int(net_io.get(key, 0) or 0) for key in ("errin", "errout", "dropin", "dropout"))

    if cpu_usage >= 90:
        health_score -= 18
        _recommend(recommendations, "CPU 占用已进入高压区，建议关闭异常高占用进程或等待任务结束后复查。")
    elif cpu_usage >= 75:
        health_score -= 10
        _recommend(recommendations, "CPU 占用偏高，建议观察 Top CPU 进程。")

    if mem_percent >= 90:
        health_score -= 18
        _recommend(recommendations, "内存压力很高，建议释放大内存应用或重启长期运行的后台程序。")
    elif mem_percent >= 75:
        health_score -= 10
        _recommend(recommendations, "内存占用偏高，建议检查 Top 内存进程。")

    if swap_percent >= 75:
        health_score -= 6
        _recommend(recommendations, "虚拟内存使用偏高，说明物理内存可能长期不足。")

    if low_disks:
        health_score -= 18
        _recommend(recommendations, "存在磁盘可用空间紧张，建议清理下载、缓存或迁移大文件。")
    elif warn_disks:
        health_score -= 8
        _recommend(recommendations, "有磁盘接近高水位，建议提前整理空间。")

    if net_errors > 0:
        health_score -= 6
        _recommend(recommendations, "网络接口存在错误包或丢弃包，建议检查网线、无线信号或驱动。")

    if uptime_days >= 14:
        health_score -= 5
        _recommend(recommendations, "系统已连续运行较久，维护窗口内重启可释放长期累积状态。")

    if battery.get("present") and not battery.get("charging") and _pct(battery.get("percentage", 0)) < 25:
        health_score -= 5
        _recommend(recommendations, "电池电量偏低且未充电，建议连接电源。")

    health_score = max(0, min(100, round(health_score)))

    critical_alerts = []
    warning_alerts = []
    for message in recommendations:
        if any(keyword in message for keyword in ("很高", "紧张", "高压")):
            critical_alerts.append(message)
        else:
            warning_alerts.append(message)
    all_alerts = critical_alerts + warning_alerts

    connected_adapters = [
        item for item in network.get("adapters", [])
        if str(item.get("Status", "")).lower() == "connected"
    ]
    dns_values = []
    for conn in network.get("connections", []):
        dns = conn.get("DNSServer")
        if isinstance(dns, list):
            dns_values.extend(str(item) for item in dns if item)
        elif dns:
            dns_values.extend(part.strip() for part in str(dns).split(",") if part.strip())
    dns_values = list(dict.fromkeys(dns_values))

    disk_total = round(sum(float(d.get("total", 0) or 0) for d in disks), 1)
    disk_used = round(sum(float(d.get("used", 0) or 0) for d in disks), 1)
    disk_percent = round((disk_used / disk_total * 100), 1) if disk_total else 0
    top_cpu = _format_processes(raw.get("processes", []))
    top_memory = _format_processes(raw.get("memory_processes") or raw.get("processes", []))
    services_supported = services.get("supported", False)

    if health_score >= 85:
        score_severity = "ok"
    elif health_score >= 70:
        score_severity = "warning"
    else:
        score_severity = "critical"

    features = [
        _feature(
            "health_score",
            "系统健康评分",
            f"{health_score}/100",
            "综合 CPU、内存、磁盘、网络错误、运行时长与电池状态计算。",
            score_severity,
            {"score": health_score},
        ),
        _feature(
            "risk_alerts",
            "关键风险提醒",
            f"{len(all_alerts)} 条",
            "；".join(all_alerts[:3]) if all_alerts else "当前未发现需要立即处理的风险。",
            "critical" if critical_alerts else "warning" if warning_alerts else "ok",
            {"alerts": all_alerts},
        ),
        _feature(
            "system_profile",
            "系统画像",
            system.get("hostname", "-"),
            f"{system.get('os', '-')} / {system.get('architecture', '-')}",
            "ok",
            system,
        ),
        _feature(
            "uptime_analysis",
            "连续运行分析",
            f"{uptime_days} 天",
            f"启动时间：{system.get('boot_time', '-')}",
            "warning" if uptime_days >= 14 else "ok",
            {"uptime_days": uptime_days, "uptime": system.get("uptime", "")},
        ),
        _feature(
            "cpu_load",
            "CPU 负载",
            f"{cpu_usage}%",
            f"{cpu.get('physical_cores', 0)} 物理核心 / {cpu.get('logical_cores', 0)} 逻辑核心，当前频率 {cpu.get('frequency_current', 0)} MHz。",
            _severity_by_percent(cpu_usage, 75, 90),
            cpu,
        ),
        _feature(
            "cpu_core_heatmap",
            "CPU 核心热力",
            f"{len(cpu.get('cores', []))} 核心",
            "展示每个逻辑核心当前负载，用于发现单核瓶颈。",
            _severity_by_percent(max([_pct(c.get("load", 0)) for c in cpu.get("cores", [])] or [0]), 75, 90),
            {"cores": cpu.get("cores", [])},
        ),
        _feature(
            "memory_pressure",
            "内存压力",
            f"{mem_percent}%",
            f"总计 {_gb(memory.get('total_gb', 0))}，可用 {_gb(memory.get('available_gb', 0))}。",
            _severity_by_percent(mem_percent, 75, 90),
            memory,
        ),
        _feature(
            "swap_pressure",
            "虚拟内存压力",
            f"{swap_percent}%",
            f"虚拟内存总计 {_gb(swap.get('total_gb', 0))}，已用 {_gb(swap.get('used_gb', 0))}。",
            _severity_by_percent(swap_percent, 75, 90),
            swap,
        ),
        _feature(
            "disk_summary",
            "磁盘总览",
            f"{disk_percent}%",
            f"{len(disks)} 个分区，总容量 {_gb(disk_total)}，已用 {_gb(disk_used)}。",
            _severity_by_percent(disk_percent, 80, 92),
            {"total_gb": disk_total, "used_gb": disk_used, "percent": disk_percent, "disks": disks},
        ),
        _feature(
            "disk_low_space",
            "磁盘空间预警",
            f"{len(low_disks)} 个紧张",
            "；".join(f"{d.get('device', '?')} 剩余 {_gb(d.get('free', 0))}" for d in low_disks[:4])
            if low_disks else "未发现 90% 以上使用率分区。",
            "critical" if low_disks else "warning" if warn_disks else "ok",
            {"critical": low_disks, "warning": warn_disks},
        ),
        _feature(
            "storage_io",
            "存储 I/O 累计",
            f"读 {_gb(raw.get('disk_io', {}).get('read_mb', 0) / 1024)}",
            f"累计写入 {_gb(raw.get('disk_io', {}).get('write_mb', 0) / 1024)}，读写次数 {raw.get('disk_io', {}).get('read_count', 0)} / {raw.get('disk_io', {}).get('write_count', 0)}。",
            "info",
            raw.get("disk_io", {}),
        ),
        _feature(
            "network_throughput",
            "网络吞吐累计",
            f"收 {_gb(net_io.get('bytes_recv_mb', 0) / 1024)}",
            f"累计发送 {_gb(net_io.get('bytes_sent_mb', 0) / 1024)}，包数量 {net_io.get('packets_sent', 0)} / {net_io.get('packets_recv', 0)}。",
            "info",
            net_io,
        ),
        _feature(
            "network_errors",
            "网络错误计数",
            f"{net_errors}",
            f"错误入/出 {net_io.get('errin', 0)} / {net_io.get('errout', 0)}，丢弃入/出 {net_io.get('dropin', 0)} / {net_io.get('dropout', 0)}。",
            "warning" if net_errors else "ok",
            net_io,
        ),
        _feature(
            "active_connections",
            "活动连接",
            f"{connections.get('total', 0)}",
            f"已建立 {connections.get('established', 0)}，监听 {connections.get('listening', 0)}。",
            "info",
            connections,
        ),
        _feature(
            "interface_inventory",
            "网卡清单",
            f"{len(connected_adapters)} 个在线",
            f"共发现 {len(network.get('adapters', []))} 个已启用适配器。",
            "ok" if connected_adapters else "warning",
            {"adapters": network.get("adapters", []), "connected": connected_adapters},
        ),
        _feature(
            "dns_snapshot",
            "DNS 快照",
            f"{len(dns_values)} 个",
            "、".join(dns_values[:4]) if dns_values else "未读取到 DNS 服务器。",
            "ok" if dns_values else "warning",
            {"servers": dns_values},
        ),
        _feature(
            "top_cpu_processes",
            "Top CPU 进程",
            top_cpu[0]["name"] if top_cpu else "无数据",
            f"最高 CPU 占用 {top_cpu[0]['cpu']}%。" if top_cpu else "暂未读取到进程数据。",
            "warning" if top_cpu and top_cpu[0]["cpu"] >= 50 else "info",
            {"processes": top_cpu},
        ),
        _feature(
            "top_memory_processes",
            "Top 内存进程",
            top_memory[0]["name"] if top_memory else "无数据",
            f"最高内存占用 {top_memory[0]['memory_mb']} MB。" if top_memory else "暂未读取到进程数据。",
            "warning" if top_memory and top_memory[0]["memory_mb"] >= 1024 else "info",
            {"processes": top_memory},
        ),
        _feature(
            "service_summary",
            "服务运行摘要",
            f"{services.get('running', 0)} 运行中" if services_supported else "不支持",
            f"共 {services.get('total', 0)} 个服务，停止 {services.get('stopped', 0)}，暂停 {services.get('paused', 0)}。"
            if services_supported else "当前平台无法读取 Windows 服务状态。",
            "info" if services_supported else "warning",
            services,
        ),
        _feature(
            "battery_runtime",
            "电池续航",
            f"{battery.get('percentage', 0)}%" if battery.get("present") else "无电池",
            _battery_detail(battery),
            "warning" if battery.get("present") and not battery.get("charging") and _pct(battery.get("percentage", 0)) < 25 else "ok",
            battery,
        ),
    ]

    feature_map = {item["id"]: item for item in features}
    ordered_features = [feature_map[feature_id] for feature_id in FEATURE_IDS]
    summary_status = "健康" if score_severity == "ok" else "需关注" if score_severity == "warning" else "需处理"

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "feature_count": len(ordered_features),
        "summary": {
            "health_score": health_score,
            "status": summary_status,
            "critical_count": len(critical_alerts),
            "warning_count": len(warning_alerts),
            "recommendations": recommendations[:6],
        },
        "features": ordered_features,
    }


def _battery_detail(battery):
    if not battery.get("present"):
        return "台式机或未检测到电池。"
    charging = "充电中" if battery.get("charging") else "未充电"
    secsleft = battery.get("secsleft")
    if isinstance(secsleft, (int, float)) and secsleft > 0 and secsleft < 10 ** 8:
        hours = int(secsleft // 3600)
        minutes = int((secsleft % 3600) // 60)
        return f"{charging}，预计剩余 {hours} 小时 {minutes} 分钟。"
    return f"{charging}，系统未提供剩余时长。"


def get_insights_snapshot():
    return compose_insights(collect_insight_raw())
