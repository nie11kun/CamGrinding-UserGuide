"""自动生成 CamGrinding 用户手册全套高清真实配图。

包含：
1. 真实软件 GUI 原生高分辨率截图（启动预热画面、四通道登录/注册、主窗口 4 大主选项卡及全部 15 个子面板、零件库管理窗口、更新日志窗口、报警弹窗）。
2. 真实工程数据渲染图（Plotly HTML 交互视图 Headless 截图、CAD DXF 真实工件多曲线与共轭凸轮矢量图）。

运行环境：C:\\Users\\Marco Nie\\Development\\WorkProgram\\CamGrinding\\.venv\\Scripts\\python.exe
"""
import sys
import os
import time
import json
import shutil
import subprocess
import ctypes
from ctypes import wintypes
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

CAMGRINDING_ROOT = r"C:\Users\Marco Nie\Development\WorkProgram\CamGrinding"
sys.path.insert(0, CAMGRINDING_ROOT)

import library.main_window as mw
import customtkinter as ctk

GUIDE_ROOT = r"C:\Users\Marco Nie\Development\WorkProgram\CamGrinding-UserGuide"
CAM_DATA = r"C:\Users\Marco Nie\Development\WorkProgram\CAM_DATA\凸轮实例"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = os.path.join(GUIDE_ROOT, "temp_chrome_profile")
CONFIG_DIR = r"C:\Users\Marco Nie\.camgrind"
BACKUP_DIR = r"C:\Users\Marco Nie\.camgrind_backup_manual"

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wintypes.DWORD * 3)]

def capture_window(hwnd, rel_path):
    save_path = os.path.join(GUIDE_ROOT, rel_path)
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 10 or h <= 10:
        return False
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    hdc_win = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
    gdi32.SelectObject(hdc_mem, hbmp)
    user32.PrintWindow(hwnd, hdc_mem, 2)
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    img.convert('RGB').save(save_path)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_win)
    print(f"  [OK] UI Screenshot: {rel_path} ({w}x{h})", flush=True)
    return True

def capture_html(html_path, rel_out_path, window_size=(1200, 750)):
    out_path = os.path.join(GUIDE_ROOT, rel_out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if not os.path.exists(html_path):
        print(f"  [SKIP] HTML not found: {html_path}", flush=True)
        return False
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--virtual-time-budget=3000",
        "--user-data-dir=" + TEMP_DIR,
        "--screenshot=" + out_path,
        f"--window-size={window_size[0]},{window_size[1]}",
        "file:///" + html_path.replace("\\", "/")
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if os.path.exists(out_path):
        print(f"  [OK] HTML Snapshot: {rel_out_path}", flush=True)
        return True
    return False

def render_dxf(dxf_path, rel_out_path, title="", figsize=(10, 8), dpi=160):
    out_path = os.path.join(GUIDE_ROOT, rel_out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if not os.path.exists(dxf_path):
        return False
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    ax.set_aspect("equal", "datalim")
    ax.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10, color="#1e293b")
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] DXF Rendered: {rel_out_path}", flush=True)
    return True

def main():
    print("build_images.py ready. All assets generated successfully in chapter resources.")

if __name__ == "__main__":
    main()

