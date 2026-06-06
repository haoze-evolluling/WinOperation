"""GPU hardware information service.

Supports multi-vendor detection (NVIDIA, AMD, Intel) with automatic
fallback chains: GPUtil -> nvidia-smi -> WMI + typeperf.
"""

import subprocess

from .system_info import _wmi  # reuse WMI connection from system_info
from utils import CREATE_NO_WINDOW

try:
    import GPUtil
except ImportError:
    GPUtil = None

def _typeperf_gpu_load():
    """Return the max GPU engine utilization (%) via typeperf, or None."""
    try:
        cmd = 'typeperf "\\GPU Engine(*)\\Utilization Percentage" -sc 1'
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.check_output(
            cmd, startupinfo=startupinfo, shell=True, timeout=10
        ).decode("gbk", errors="ignore")

        lines = [line.strip() for line in output.strip().split("\n") if line.strip()]
        data_line = None
        for line in reversed(lines):
            if "," in line and any(c.isdigit() for c in line):
                data_line = line.replace('"', "")
                break
        if data_line:
            values = data_line.split(",")
            floats = []
            for v in values[1:]:
                try:
                    floats.append(float(v))
                except ValueError:
                    continue
            if floats:
                return min(round(max(floats), 1), 100.0)
    except Exception:
        pass
    return None


def _nvidia_smi_gpus():
    """Query all NVIDIA GPUs via nvidia-smi.

    Returns a list of dicts, one per GPU, or empty list on failure.
    """
    try:
        out = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,memory.total,memory.used,"
                "temperature.gpu,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            creationflags=CREATE_NO_WINDOW,
        ).stdout.strip()
        if not out:
            return []
        gpus = []
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 7:
                continue
            idx, name, gpu_usage, vram_total, vram_used, temp, driver_ver = parts[:7]
            vram_total_f = max(float(vram_total or 0), 0)
            vram_used_f = max(float(vram_used or 0), 0)
            gpus.append(
                {
                    "name": name,
                    "vendor": "NVIDIA",
                    "dedicated": True,
                    "load": min(max(float(gpu_usage or 0), 0), 100),
                    "temperature": float(temp) if temp else None,
                    "vram_total": vram_total_f,
                    "vram_used": vram_used_f,
                    "vram_percent": (
                        round((vram_used_f / vram_total_f) * 100, 1)
                        if vram_total_f > 0
                        else 0
                    ),
                    "driver_version": driver_ver or "",
                }
            )
        return gpus
    except Exception:
        return []


def _gpUtil_gpus():
    """Query NVIDIA GPUs via the GPUtil library (richer data).

    Falls back to nvidia-smi if GPUtil is not installed.
    """
    if not GPUtil:
        return _nvidia_smi_gpus()
    try:
        raw = GPUtil.getGPUs()
        if not raw:
            return _nvidia_smi_gpus()
        gpus = []
        for gpu in raw:
            vram_total = max(float(gpu.memoryTotal or 0), 0)
            vram_used = max(float(gpu.memoryUsed or 0), 0)
            gpus.append(
                {
                    "name": gpu.name,
                    "vendor": "NVIDIA",
                    "dedicated": True,
                    "load": min(round(gpu.load * 100, 1), 100),
                    "temperature": float(gpu.temperature) if gpu.temperature is not None else None,
                    "vram_total": vram_total,
                    "vram_used": vram_used,
                    "vram_percent": (
                        round((vram_used / vram_total) * 100, 1)
                        if vram_total > 0
                        else 0
                    ),
                    "driver_version": "",
                }
            )
        # GPUtil doesn't expose driver version; backfill from nvidia-smi if possible
        smi = _nvidia_smi_gpus()
        if smi and smi[0].get("driver_version"):
            ver = smi[0]["driver_version"]
            for g in gpus:
                g["driver_version"] = ver
        return gpus
    except Exception:
        return _nvidia_smi_gpus()


def _wmi_non_nvidia_gpus(nvidia_names):
    """Query non-NVIDIA GPUs via WMI.

    *nvidia_names* — a set of GPU name strings already reported by NVIDIA
    detection, used for deduplication.
    """
    try:
        wmi_svc = _wmi()
        controllers = wmi_svc.ExecQuery("SELECT Name, AdapterRAM FROM Win32_VideoController")
    except Exception:
        return []

    results = []
    known = {n.upper() for n in nvidia_names}

    for ctrl in controllers:
        name = (ctrl.Name or "").strip()
        uname = name.upper()
        if not name:
            continue
        # skip virtual / already-logged
        if any(kw in uname for kw in ("DRIVER", "VIRTUAL")):
            continue
        if "NVIDIA" in uname or any(nv in uname for nv in known):
            continue

        # classify
        dedicated = False
        vendor = "Other"
        if "INTEL" in uname:
            vendor = "Intel"
            if "ARC" in uname:
                dedicated = True
        elif "AMD" in uname or "RADEON" in uname:
            vendor = "AMD"
            if any(x in uname for x in ("RX ", "XT ", "PRO ", "FIREPRO", "W7000", "W6000")):
                dedicated = True

        # load via typeperf
        load = _typeperf_gpu_load()

        # VRAM: WMI AdapterRAM often capped at 4 GB — note the limitation
        ram_bytes = int(getattr(ctrl, "AdapterRAM", 0) or 0)
        ram_mb = ram_bytes / (1024 ** 2)

        results.append(
            {
                "name": name,
                "vendor": vendor,
                "dedicated": dedicated,
                "load": load if load is not None else 0,
                "temperature": None,
                "vram_total": ram_mb if 0 < ram_mb <= 32000 else None,
                "vram_used": None,
                "vram_percent": None,
                "driver_version": "",
            }
        )
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_gpu_detail():
    """Return a unified list of dicts for every detected GPU.

    Priority:
      1. NVIDIA GPUs via GPUtil (or nvidia-smi fallback)
      2. Other GPUs (AMD, Intel, etc.) via WMI + typeperf

    Returns:
        {"gpus": [{name, vendor, dedicated, load, temperature,
                    vram_total, vram_used, vram_percent, driver_version}, ...]}
    """
    nvidia_gpus = _gpUtil_gpus()
    nvidia_names = {g["name"] for g in nvidia_gpus}
    other_gpus = _wmi_non_nvidia_gpus(nvidia_names)

    all_gpus = nvidia_gpus + other_gpus
    return {"gpus": all_gpus}


def get_gpu_names():
    """Return a lightweight list of GPU names (for the hardware info card).

    Compatible with the existing ``system_info.get_gpu_names`` signature.
    """
    detail = get_gpu_detail()
    return [{"name": g["name"]} for g in detail.get("gpus", [])]


if __name__ == "__main__":
    import json

    result = get_gpu_detail()
    print(json.dumps(result, indent=2, ensure_ascii=False))
