import locale
import re
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Blueprint, request, jsonify
from utils import CREATE_NO_WINDOW

speedtest_bp = Blueprint("speedtest", __name__)

DOMESTIC_SITES = [
    ("百度", "www.baidu.com"),
    ("腾讯", "www.qq.com"),
    ("淘宝", "www.taobao.com"),
    ("京东", "www.jd.com"),
    ("新浪", "www.sina.com.cn"),
    ("搜狐", "www.sohu.com"),
    ("网易", "www.163.com"),
    ("天猫", "www.tmall.com"),
    ("B站", "www.bilibili.com"),
    ("微博", "www.weibo.com"),
    ("知乎", "www.zhihu.com"),
    ("CSDN", "www.csdn.net"),
    ("阿里云", "www.aliyun.com"),
    ("小米", "www.xiaomi.com"),
    ("华为", "www.huawei.com"),
    ("美团", "www.meituan.com"),
    ("抖音", "www.douyin.com"),
    ("豆瓣", "www.douban.com"),
    ("爱奇艺", "www.iqiyi.com"),
    ("携程", "www.ctrip.com"),
]

FOREIGN_SITES = [
    ("Google", "www.google.com"),
    ("YouTube", "www.youtube.com"),
    ("Facebook", "www.facebook.com"),
    ("Twitter/X", "www.twitter.com"),
    ("Instagram", "www.instagram.com"),
    ("LinkedIn", "www.linkedin.com"),
    ("GitHub", "www.github.com"),
    ("StackOverflow", "stackoverflow.com"),
    ("Reddit", "www.reddit.com"),
    ("Wikipedia", "www.wikipedia.org"),
    ("Amazon", "www.amazon.com"),
    ("Microsoft", "www.microsoft.com"),
    ("Apple", "www.apple.com"),
    ("Netflix", "www.netflix.com"),
    ("Cloudflare", "www.cloudflare.com"),
    ("Docker", "www.docker.com"),
    ("Python", "www.python.org"),
    ("Nginx", "www.nginx.com"),
    ("Apache", "www.apache.org"),
    ("Figma", "www.figma.com"),
]

# Common encodings for Windows console output
_CONSOLE_ENCODINGS = [
    locale.getpreferredencoding(),
    "utf-8",
    "gbk",
    "gb2312",
    "cp936",
    "cp437",
    "cp850",
]


def _decode_output(raw):
    for enc in _CONSOLE_ENCODINGS:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def parse_ping_output(output, host):
    result = {
        "host": host, "ip": "", "sent": 0, "received": 0,
        "loss_rate": 100, "min_ms": None, "max_ms": None, "avg_ms": None,
        "status": "unknown",
    }

    ip_match = re.search(r"\[([^\]]+)\]", output)
    if ip_match:
        raw_ip = ip_match.group(1)
        if re.match(r"^[\d\.]+$", raw_ip) or re.match(r"^[0-9a-fA-F:]+$", raw_ip):
            result["ip"] = raw_ip

    if "could not find host" in output.lower() or "找不到主机" in output:
        result["status"] = "dns_fail"
        return result

    # Match packet statistics: Sent/已发送, Received/已接收, Lost/丢失
    sent_m = re.search(r"(?:Sent|已发送)\s*=\s*(\d+)", output)
    recv_m = re.search(r"(?:Received|已接收)\s*=\s*(\d+)", output)
    loss_m = re.search(r"(?:Lost|丢失)\s*=\s*(\d+)\s*\((\d+)%", output)

    if sent_m:
        result["sent"] = int(sent_m.group(1))
    if recv_m:
        result["received"] = int(recv_m.group(1))
    if loss_m:
        result["loss_rate"] = int(loss_m.group(2))

    # Fallback: extract from statistics line if patterns didn't match
    if not sent_m:
        stat_sent = re.search(r"=\s*(\d+)\s*[,，]", output)
        if stat_sent:
            result["sent"] = int(stat_sent.group(1))
    if not recv_m:
        stat_recv = re.search(r"[,，]\s*=\s*(\d+)", output)
        if stat_recv:
            result["received"] = int(stat_recv.group(1))

    # Match round-trip times: Minimum/最短, Maximum/最长, Average/平均
    min_m = re.search(r"(?:Minimum|最短)\s*=\s*(\d+)", output)
    max_m = re.search(r"(?:Maximum|最长)\s*=\s*(\d+)", output)
    avg_m = re.search(r"(?:Average|平均)\s*=\s*(\d+)", output)

    if min_m:
        result["min_ms"] = int(min_m.group(1))
    if max_m:
        result["max_ms"] = int(max_m.group(1))
    if avg_m:
        result["avg_ms"] = int(avg_m.group(1))

    if result["loss_rate"] == 100:
        result["status"] = "timeout"
    elif result["loss_rate"] > 0:
        result["status"] = "partial"
    else:
        result["status"] = "ok"

    return result


def ping_host(name, host, count=2, timeout=3000):
    try:
        cmd = ["ping", "-n", str(count), "-w", str(timeout), host]
        proc = subprocess.run(
            cmd, capture_output=True,
            timeout=count * (timeout // 1000 + 1) + 2,
            creationflags=CREATE_NO_WINDOW,
        )
        raw = proc.stdout + proc.stderr
        output = _decode_output(raw)

        r = parse_ping_output(output, host)
        r["name"] = name
        return r

    except subprocess.TimeoutExpired:
        return {"name": name, "host": host, "ip": "", "sent": count, "received": 0,
                "loss_rate": 100, "min_ms": None, "max_ms": None, "avg_ms": None,
                "status": "timeout"}
    except Exception:
        return {"name": name, "host": host, "ip": "", "sent": count, "received": 0,
                "loss_rate": 100, "min_ms": None, "max_ms": None, "avg_ms": None,
                "status": "error"}


@speedtest_bp.route("/api/speedtest", methods=["POST"])
def run_speedtest():
    data = request.get_json() or {}
    group = data.get("group", "all")

    targets = []
    if group in ("all", "domestic"):
        targets.extend(("domestic", n, h) for n, h in DOMESTIC_SITES)
    if group in ("all", "foreign"):
        targets.extend(("foreign", n, h) for n, h in FOREIGN_SITES)

    domestic = []
    foreign = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        fut_map = {executor.submit(ping_host, n, h): (g, n)
                   for g, n, h in targets}
        for future in as_completed(fut_map):
            g, _ = fut_map[future]
            try:
                r = future.result()
            except Exception:
                continue
            if g == "domestic":
                domestic.append(r)
            else:
                foreign.append(r)

    domestic.sort(key=lambda x: x["name"])
    foreign.sort(key=lambda x: x["name"])

    return jsonify({
        "success": True,
        "data": {"domestic": domestic, "foreign": foreign},
    })


@speedtest_bp.route("/api/speedtest/custom", methods=["POST"])
def custom_speedtest():
    data = request.get_json() or {}
    target = (data.get("target") or "").strip()
    action = data.get("action", "ping")

    if not target:
        return jsonify({"success": False, "message": "请输入目标 IP 或域名"}), 400

    result = {"target": target, "nslookup": None, "ping": None}

    if action in ("nslookup", "all"):
        try:
            out = subprocess.run(
                ["nslookup", target], capture_output=True, text=False, timeout=10,
                creationflags=CREATE_NO_WINDOW,
            )
            raw = _decode_output(out.stdout + out.stderr)
            result["nslookup"] = raw.strip()
        except subprocess.TimeoutExpired:
            result["nslookup"] = "nslookup 命令执行超时"
        except Exception as e:
            result["nslookup"] = f"nslookup 执行失败: {e}"

    if action in ("ping", "all"):
        ping_result = ping_host(target, target, count=4, timeout=3000)
        result["ping"] = ping_result

    return jsonify({"success": True, "data": result})


@speedtest_bp.route("/api/speedtest/resolve", methods=["POST"])
def resolve_target():
    data = request.get_json() or {}
    target = (data.get("target") or "").strip()
    if not target:
        return jsonify({"success": False, "message": "请输入要解析的域名或 IP"}), 400

    started = time.perf_counter()
    try:
        infos = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        return jsonify({
            "success": True,
            "data": {
                "target": target,
                "addresses": [],
                "elapsed_ms": elapsed_ms,
                "error": str(exc),
                "status": "failed",
            },
        })

    addresses = []
    seen = set()
    for family, _, _, _, sockaddr in infos:
        ip = sockaddr[0]
        if ip in seen:
            continue
        seen.add(ip)
        addresses.append({
            "ip": ip,
            "family": "IPv6" if family == socket.AF_INET6 else "IPv4",
        })

    return jsonify({
        "success": True,
        "data": {
            "target": target,
            "addresses": addresses,
            "elapsed_ms": elapsed_ms,
            "error": "",
            "status": "ok" if addresses else "empty",
        },
    })
