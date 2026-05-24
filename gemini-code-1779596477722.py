import os
import sys
import subprocess

# 安全导入依赖
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import wmi
except ImportError:
    wmi = None

# ==============================================================================
# 核心功能1：【已修复】优化后的非英伟达负载获取算法（解决行尾提示语Bug）
# ==============================================================================
def get_non_nvidia_load():
    """
    通过系统的 typeperf 性能计数器快速抓取当前 GPU 引擎的总使用率。
    """
    try:
        cmd = 'typeperf "\\GPU Engine(*)\\Utilization Percentage" -sc 1'
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        output = subprocess.check_output(cmd, startupinfo=startupinfo, shell=True).decode('gbk', errors='ignore')
        # 过滤空行并切分
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        
        # 【Bug修复点】：从后往前遍历，跳过“命令成功完成”等系统提示语，寻找真正的数据行
        data_line = None
        for line in reversed(lines):
            if ',' in line and any(char.isdigit() for char in line):
                data_line = line.replace('"', '')
                break
                
        if data_line:
            values = data_line.split(',')
            float_vals = []
            for v in values[1:]:
                try:
                    float_vals.append(float(v))
                except ValueError:
                    continue
            if float_vals:
                total_load = max(float_vals)
                return min(round(total_load, 1), 100.0)
    except Exception:
        pass
    return "0.0"

# ==============================================================================
# 核心功能2：【已升级】多卡并行扫描（支持 NVIDIA独显 / AMD独显 / 智能核显分类）
# ==============================================================================
def get_optimized_gpu_info():
    print("=" * 60)
    print("         GPU 硬件状态实时监测系统 (多卡并行·终极修复版)")
    print("=" * 60)

    already_logged_gpus = []  # 全局去重池，记录已精密打印过的独立显卡

    # 1. 探测并高亮打印 NVIDIA 独立显卡
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                for i, gpu in enumerate(gpus):
                    already_logged_gpus.append(gpu.name.upper())
                    print(f" 🟢【独立显卡】NVIDIA 设备 #{i}")
                    print(f" ----------------------------------------")
                    print(f"  显卡型号: {gpu.name}")
                    print(f"  工作负载: {gpu.load * 100:.1f} %")
                    print(f"  核心温度: {gpu.temperature} °C")
                    print(f"  已用显存: {gpu.memoryUsed:.0f} MB / {gpu.memoryTotal:.0f} MB")
                    print(f"  显存利用: {(gpu.memoryUsed / gpu.memoryTotal) * 100:.1f} %")
                    print("=" * 60)
        except Exception as e:
            print(f"  NVIDIA 精密驱动调用异常: {e}")

    # 2. 探测系统其他适配器（智能识别 AMD 独显、Intel 独显及各类核显）
    if wmi:
        try:
            c = wmi.WMI()
            video_controllers = c.Win32_VideoController()
            
            for controller in video_controllers:
                name = controller.Name
                uname = name.upper()
                
                # 过滤虚拟显卡
                if "DRIVER" in uname or "VIRTUAL" in uname:
                    continue
                    
                # 全局去重：如果已经在上面英伟达区域打印过了，直接跳过
                if any(nv_name in uname for nv_name in already_logged_gpus) or "NVIDIA" in uname:
                    continue

                # 【升级点】：智能划分显卡身份（独立显卡 vs 集成显卡）
                is_dedicated = False
                if "INTEL" in uname:
                    vendor = "Intel (英特尔)"
                    if "ARC" in uname:  # 识别英特尔蓝戟等独显
                        is_dedicated = True
                elif "AMD" in uname or "RADEON" in uname:
                    vendor = "AMD"
                    # 识别常见 AMD 独显系列关键字
                    if any(x in uname for x in ["RX ", "XT ", "PRO ", "FIREPRO", "W7000", "W6000"]):
                        is_dedicated = True
                else:
                    vendor = "其他厂商"

                # 动态生成标签
                if is_dedicated:
                    print(f" 🔴【独立显卡】{vendor} 设备")
                else:
                    print(f" 🔵【集成显卡】{vendor} 设备")
                    
                print(f" ----------------------------------------")
                print(f"  显卡型号: {name}")
                
                # 智能计算实时负载
                load = get_non_nvidia_load()
                load_info = f"{load}%" if isinstance(load, (float, int)) else load
                print(f"  工作负载: {load_info}")
                
                # 温度呈现优化
                if is_dedicated:
                    print(f"  核心温度: 需配合厂商软件查看 (底边WMI未开放独显温度外部接口)")
                else:
                    print(f"  核心温度: 暂不支持 (核显温度共享CPU温度)")

                # 显存展示优化（解决 4GB 截断与动态共享显示）
                ram_bytes = int(controller.AdapterRAM or 0)
                ram_mb = ram_bytes / (1024 ** 2)
                
                if ram_mb <= 0 or ram_mb > 32000:
                    print(f"  显存模式: Windows 动态共享托管 (智能调用物理内存)")
                elif is_dedicated and (3990 <= ram_mb <= 4100):
                    # 触发 WMI 4GB 溢出锁死警告
                    print(f"  物理显存: ≥ 4096 MB (受系统底层WMI限制显示为4GB，实际请参考任务管理器)")
                else:
                    print(f"  物理显存: {ram_mb:.0f} MB")
                print("=" * 60)
        except Exception as e:
            print(f"  系统底层扫描异常: {e}")

# ==============================================================================
# 主程序入口
# ==============================================================================
if __name__ == "__main__":
    try:
        get_optimized_gpu_info()
    except Exception as final_err:
        print(f"\n[崩溃拦截] 程序在运行时发生未知错误: {final_err}")
    finally:
        print("\n" + "." * 60)
        print(" [状态]: 数据检测已完成。请按回车键 [Enter] 安全退出...")
        print("." * 60)
        input()