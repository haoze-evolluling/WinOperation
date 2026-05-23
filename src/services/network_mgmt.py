import ctypes
import subprocess
from win32com.client import Dispatch
from utils import CREATE_NO_WINDOW


def _wmi():
    locator = Dispatch("WbemScripting.SWbemLocator")
    return locator.ConnectServer(".", "root/cimv2")


def get_network_status():
    """Return (adapters_list, connections_list) matching existing API shape.

    adapters: [{Name, InterfaceDescription, Status, InterfaceIndex}, ...]
    connections: [{InterfaceAlias, InterfaceDescription, IPv4Address,
                   IPv4DefaultGateway, DNSServer}, ...]
    """
    adapters = []
    connections = []

    try:
        wmi_svc = _wmi()
        for na in wmi_svc.ExecQuery(
            "SELECT Name, Description, NetConnectionStatus, InterfaceIndex "
            "FROM Win32_NetworkAdapter WHERE NetEnabled=True"
        ):
            status_map = {0: "Disconnected", 1: "Connected", 2: "Connected",
                          3: "Disconnected", 4: "Disconnected", 5: "Connecting",
                          6: "Connecting", 7: "Disconnected", 8: "Disconnected",
                          9: "Authenticating", 10: "Testing", 11: "Disconnected",
                          12: "Disconnected"}
            status = status_map.get(na.NetConnectionStatus, "Unknown")
            adapters.append({
                "Name": na.Name or "",
                "InterfaceDescription": na.Description or "",
                "Status": status,
                "InterfaceIndex": na.InterfaceIndex or 0,
            })
    except Exception:
        pass

    try:
        wmi_svc = _wmi()
        for cfg in wmi_svc.ExecQuery(
            "SELECT Description, IPAddress, DefaultIPGateway, DNSServerSearchOrder "
            "FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled=True"
        ):
            ip_list = cfg.IPAddress or []
            gw_list = cfg.DefaultIPGateway or []
            dns_list = cfg.DNSServerSearchOrder or []

            connections.append({
                "InterfaceAlias": cfg.Description or "",
                "InterfaceDescription": cfg.Description or "",
                "IPv4Address": ", ".join(ip for ip in ip_list if "." in ip),
                "IPv4DefaultGateway": gw_list[0] if gw_list else "",
                "DNSServer": ", ".join(dns_list),
            })
    except Exception:
        pass

    return adapters, connections


def toggle_wifi(enable: bool):
    """Enable or disable the Wi-Fi adapter. Returns (success, message)."""
    action = "启用" if enable else "禁用"
    try:
        wmi_svc = _wmi()
        for na in wmi_svc.ExecQuery(
            "SELECT Name, NetConnectionID FROM Win32_NetworkAdapter "
            "WHERE AdapterTypeID=0 AND PhysicalAdapter=True"
        ):
            name = (na.Name or "").lower()
            net_name = (na.NetConnectionID or "").lower()
            if any(kw in name or kw in net_name for kw in ("wi-fi", "无线", "wlan")):
                if enable:
                    result = na.Enable()
                else:
                    result = na.Disable()
                if result == 0:
                    return (True, f"WiFi 已{action}")
                return (False, f"操作返回错误码: {result}")
        return (False, "未找到无线网卡")
    except Exception as e:
        return (False, f"操作失败: {e}")


def set_dns(adapter_name: str, dns_servers: list):
    """Set DNS servers for a named adapter. Empty list = reset to auto.

    Returns (success, message).
    """
    import winreg

    try:
        wmi_svc = _wmi()
        adapter_guid = None
        for cfg in wmi_svc.ExecQuery(
            "SELECT Description, SettingID FROM Win32_NetworkAdapterConfiguration "
            "WHERE IPEnabled=True"
        ):
            if cfg.Description and adapter_name.strip() in cfg.Description:
                adapter_guid = cfg.SettingID
                break

        if not adapter_guid:
            return (False, "未找到指定的适配器")

        key_path = (
            f"SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"
            f"\\{adapter_guid}"
        )

        if not dns_servers:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                    winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
                )
                winreg.DeleteValue(key, "NameServer")
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
            flush_dns_cache()
            return (True, "DNS 已设置为: 自动获取")
        else:
            servers_str = ",".join(dns_servers)
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "NameServer", 0, winreg.REG_SZ, servers_str)
            winreg.CloseKey(key)
            flush_dns_cache()
            return (True, f"DNS 已设置为: {', '.join(dns_servers)}")

    except Exception as e:
        return (False, f"设置 DNS 失败: {e}")


def flush_dns_cache():
    """Flush the DNS resolver cache. Returns (success, message)."""
    try:
        result = ctypes.windll.dnsapi.DnsFlushResolverCache()
        if result != 0:
            return (True, "DNS 缓存已清除")
        return (False, "清除 DNS 缓存失败")
    except Exception:
        pass
    # Fallback to ipconfig
    try:
        out = subprocess.run(
            ["ipconfig", "/flushdns"], capture_output=True,
            timeout=10, creationflags=CREATE_NO_WINDOW
        )
        if out.returncode == 0:
            return (True, "DNS 缓存已清除")
    except Exception:
        pass
    return (False, "清除 DNS 缓存失败")
