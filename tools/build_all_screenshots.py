"""全面重新生成所有软件 UI 截图，确保：
1. 传入 --ui_config full，所有菜单与所有标签页 100% 开启与构建。
2. 每一个参数输入框都预填充真实工件工程数据，绝不留白。
3. 加密狗登录页完整显示居中的“验证加密狗”按钮。
4. 更新日志窗口完整渲染版本历史与关闭按钮（杜绝黑屏）。
5. 零件库管理窗口填充脱敏真实工件记录。
6. 参数校验错误弹窗完整呈现。
"""
import sys
import os
import time
import json
import tkinter as tk
import ctypes
from ctypes import wintypes
from PIL import Image

sys.argv = ['main.py', '--ui_config', 'full']
CAMGRINDING_ROOT = r"C:\Users\Marco Nie\Development\WorkProgram\CamGrinding"
sys.path.insert(0, CAMGRINDING_ROOT)

import library.main_window as mw
import customtkinter as ctk

GUIDE_ROOT = r"C:\Users\Marco Nie\Development\WorkProgram\CamGrinding-UserGuide"

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG), ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD), ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', wintypes.LONG), ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD), ('biClrImportant', wintypes.DWORD),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wintypes.DWORD * 3)]

def capture(hwnd, rel_path):
    save_path = os.path.join(GUIDE_ROOT, rel_path)
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
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
    img.convert('RGB').save(save_path)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_win)
    print(f"  [OK] Saved: {rel_path} ({w}x{h})", flush=True)
    return True

def set_entry(entry_attr, value):
    w = getattr(mw, entry_attr, None)
    if w is None:
        return
    if isinstance(w, ctk.CTkEntry):
        w.delete(0, tk.END)
        w.insert(0, str(value))
    elif isinstance(w, (ctk.CTkOptionMenu, ctk.CTkComboBox)):
        w.set(str(value))

def populate_all_fields():
    zh = mw.current_language
    # Tab 1
    set_entry("entry_wheel_dia_max", "350.0")
    set_entry("entry_wheel_dia_fix", "1.0")
    set_entry("entry_wheel_dia_min", "300.0")
    set_entry("entry_wheel_dia_step", "5.0")
    set_entry("entry_dxf_file", "D:/CamProjects/SK722/sk722_main_cam.dxf")
    set_entry("entry_save_path", "D:/CamProjects/SK722/NC_Code")

    # Tab 2
    set_entry("entry_segment_length", "0.05")
    set_entry("entry_fit_arc_choice", zh["yes"])
    set_entry("entry_fit_arcs_choice_accuracy", "1")

    # Tab 3 Subtab 1 (XY 点位文件)
    set_entry("entry_points_file", "D:/CamProjects/CMM/sk722_points.txt")
    set_entry("entry_points_data_index", "01")
    set_entry("entry_points_exchange_xy", zh["no"])
    set_entry("entry_points_offset_x", "1.0")
    set_entry("entry_points_offset_y", "1.0")
    set_entry("entry_points_graph_rotate_angle", "0")
    set_entry("entry_points_lift_choice", zh["yes"])
    set_entry("entry_points_base_circle_radius", "20.0")
    set_entry("entry_points_lift_direction", zh["clockwise"])
    set_entry("entry_points_lift_curve_x_axis_scale", "1.0")
    set_entry("entry_points_save_shape_path", "D:/CamProjects/CMM/sk722_from_points.dxf")

    # Tab 3 Subtab 2 (CAM 数据文件)
    set_entry("entry_cam_data_file", "D:/CamProjects/EC70/ec70_cam_data.txt")
    set_entry("entry_cam_data_direction", zh["counterclockwise"])
    set_entry("entry_cam_data_type", zh["relative"])
    set_entry("entry_cam_data_offset_x", "1.0")
    set_entry("entry_cam_data_offset_y", "1.0")
    set_entry("entry_cam_data_graph_rotate_angle", "0")
    set_entry("entry_cam_data_lift_choice", zh["yes"])
    set_entry("entry_cam_data_lift_direction", zh["clockwise"])
    set_entry("entry_cam_data_lift_curve_x_axis_scale", "1.0")
    set_entry("entry_cam_data_save_shape_path", "D:/CamProjects/EC70/ec70_cam_main.dxf")

    # Tab 3 Subtab 3 (CAM 图形变换)
    set_entry("entry_cam_transform_original_cam_file", "D:/CamProjects/EC70/ec70_cam_main.dxf")
    set_entry("entry_cam_transform_size_change", "-15.0")
    set_entry("entry_cam_transform_size_change_mode", zh["normal"])
    set_entry("entry_cam_transform_offset_x", "1.0")
    set_entry("entry_cam_transform_offset_y", "1.0")
    set_entry("entry_cam_transform_graph_rotate_angle", "-72.5")
    set_entry("entry_cam_transform_save_shape_path", "D:/CamProjects/EC70/ec70_cam_sub.dxf")

    # Tab 3 Subtab 4 (CAM 共轭计算)
    set_entry("entry_cam_conjugate_calc_original_cam_file", "D:/CamProjects/SK722/sk722_main_cam.dxf")
    set_entry("entry_cam_conjugate_calc_pivot_distance", "110.0")
    set_entry("entry_cam_conjugate_calc_roller_radius", "16.0")
    set_entry("entry_cam_conjugate_calc_cam_1_pendulum_length", "75.0")
    set_entry("entry_cam_conjugate_calc_cam_2_pendulum_length", "75.0")
    set_entry("entry_cam_conjugate_calc_cam_pendulums_angle", "60.0")
    set_entry("entry_cam_conjugate_calc_save_shape_path", "D:/CamProjects/SK722/sk722_conjugate_sub.dxf")

    # Tab 4 Subtab 1 Subtab 1 (凸轮转升程曲线)
    set_entry("entry_cam_to_lift_file", "D:/CamProjects/SK722/sk722_main_cam.dxf")
    set_entry("entry_cam_to_lift_base_circle_radius", "20.0")
    set_entry("entry_cam_to_lift_meas_wheel_radius", "16.0")
    set_entry("entry_cam_to_lift_lift_direction", zh["clockwise"])
    set_entry("entry_cam_to_lift_lift_curve_x_axis_scale", "1.0")
    set_entry("entry_cam_to_lift_save_shape_path", "D:/CamProjects/SK722/sk722_lift_output.txt")

    # Tab 4 Subtab 1 Subtab 2 (升程转凸轮曲线)
    set_entry("entry_lift_to_cam_file", "D:/CamProjects/EC70/ec70_lift_curve.txt")
    set_entry("entry_lift_to_cam_base_circle_radius", "32.0")
    set_entry("entry_lift_to_cam_meas_wheel_radius", "0.0")
    set_entry("entry_lift_to_cam_lift_direction", zh["clockwise"])
    set_entry("entry_lift_to_cam_save_shape_path", "D:/CamProjects/EC70/ec70_reconstructed.dxf")

    # Tab 4 Subtab 1 Subtab 3 (速度转升程曲线)
    set_entry("entry_velocity_acc_file", "D:/CamProjects/Kinematics/valve_velocity.txt")
    set_entry("entry_velocity_acc_mode", zh["velocity"])
    set_entry("entry_velocity_acc_rotate_speed", "600")
    set_entry("entry_velocity_acc_x_axis_scale", "1.0")
    set_entry("entry_velocity_acc_save_shape_path", "D:/CamProjects/Kinematics/integrated_lift.txt")

    # Tab 4 Subtab 1 Subtab 4 (曲线转公式方程)
    set_entry("entry_fit_formula_file", "D:/CamProjects/SK722/sk722_main_cam.dxf")
    set_entry("entry_fit_formula_mode", zh["fourier"])
    set_entry("entry_fit_formula_accuracy", "0.001")
    set_entry("entry_fit_formula_save_shape_path", "D:/CamProjects/SK722/sk722_formula.txt")

    # Tab 4 Subtab 2 Subtab 1 (加工误差修正)
    set_entry("entry_deviation_fix_std_file", "D:/CamProjects/LD3600/ld3600_std.dxf")
    set_entry("entry_deviation_fix_program_file", "D:/CamProjects/LD3600/ld3600_prog_v1.dxf")
    set_entry("entry_deviation_fix_data_file", "D:/CamProjects/LD3600/ld3600_meas_v1.txt")
    set_entry("entry_deviation_fix_process_size_compensation", "0.0")
    set_entry("entry_deviation_fix_data_rotate_angle", "0.0")
    set_entry("entry_deviation_fix_save_shape_path", "D:/CamProjects/LD3600/ld3600_prog_v2.dxf")

    # Tab 4 Subtab 2 Subtab 2 (直径误差分析)
    set_entry("entry_deviation_analyze_std_file", "D:/CamProjects/LD3600/ld3600_std.dxf")
    set_entry("entry_deviation_analyze_wheel_dia_std", "350.0")
    set_entry("entry_deviation_analyze_wheel_dia_real", "330.0")

    # Tab 4 Subtab 2 Subtab 3 (CAM 误差叠加)
    set_entry("entry_error_overlay_original_cam_file", "D:/CamProjects/LD3600/ld3600_std.dxf")
    set_entry("entry_error_overlay_error_file", "D:/CamProjects/LD3600/p65_error_table.txt")
    set_entry("entry_error_overlay_error_direction", zh["normal"])
    set_entry("entry_error_overlay_save_shape_path", "D:/CamProjects/LD3600/ld3600_overlay.dxf")

    # Tab 4 Subtab 2 Subtab 4 (CAM 误差对比)
    set_entry("entry_error_compare_cam_file_1", "D:/CamProjects/LD3600/ld3600_std.dxf")
    set_entry("entry_error_compare_cam_file_2", "D:/CamProjects/LD3600/ld3600_prog_v2.dxf")
    set_entry("entry_error_compare_max_error_distance", "0.05")
    set_entry("entry_error_compare_save_shape_path", "D:/CamProjects/LD3600/ld3600_compare.txt")

    # Tab 4 Subtab 3 Subtab 1 (DXF 文件对比)
    set_entry("entry_compare_dxf_1", "D:/CamProjects/EC70/ec70_cam_main.dxf")
    set_entry("entry_compare_dxf_2", "D:/CamProjects/EC70/ec70_cam_sub.dxf")

    # Tab 4 Subtab 3 Subtab 2 (DXF 离散化)
    set_entry("entry_dxf_discretization_file_path", "D:/CamProjects/SK722/sk722_spline.dxf")
    set_entry("entry_discretization_shape_num", "3600")
    set_entry("entry_discretization_curve_direction", "顺时针，从X轴正半轴开始")

    # Tab 4 Subtab 3 Subtab 3 (DXF 拟合圆弧)
    set_entry("entry_dxf_fit_arcs_file_path", "D:/CamProjects/SK722/sk722_discrete.dxf")
    set_entry("entry_fit_arcs_accuracy", "1.0")

def snap_main_tabs(root):
    zh = mw.current_language
    hwnd = root.winfo_id()

    # 1. 基本参数
    mw.tabview.set(zh["tabview_1"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "2_code_generation/resources/tab_basic_params.png")
    capture(hwnd, "1_getting_started/resources/ui_overview.png")

    # 2. 高级参数
    mw.tabview.set(zh["tabview_2"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "2_code_generation/resources/tab_advanced_params.png")

    # 3. 绘图参数
    mw.tabview.set(zh["tabview_3"])
    root.update()
    time.sleep(0.1)

    # 3.1 XY 点位文件
    mw.tab3_sub_tabview.set(zh["tab3_subtab_1"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "3_cam_drawing/resources/tab_xy_points.png")

    # 3.2 CAM 数据文件
    mw.tab3_sub_tabview.set(zh["tab3_subtab_2"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "3_cam_drawing/resources/tab_cam_data.png")

    # 3.3 CAM 图形变换
    mw.tab3_sub_tabview.set(zh["tab3_subtab_3"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "3_cam_drawing/resources/tab_cam_transform.png")

    # 3.4 CAM 共轭计算
    mw.tab3_sub_tabview.set(zh["tab3_subtab_4"])
    root.update()
    time.sleep(0.15)
    root.update()
    capture(hwnd, "3_cam_drawing/resources/tab_cam_conjugate.png")

    # 4. 工具箱
    mw.tabview.set(zh["tabview_4"])
    root.update()
    time.sleep(0.1)

    # 4.1 凸轮分析
    mw.tab4_sub_tabview.set(zh["tab4_subtab_1"])
    root.update()
    time.sleep(0.1)
    mw.tab4_subtab1_sub_tabview.set(zh["tab4_subtab1_subtab_1"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "4_toolbox_analysis/resources/tab_cam_to_lift.png")

    mw.tab4_subtab1_sub_tabview.set(zh["tab4_subtab1_subtab_2"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "4_toolbox_analysis/resources/tab_lift_to_cam.png")

    mw.tab4_subtab1_sub_tabview.set(zh["tab4_subtab1_subtab_3"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "4_toolbox_analysis/resources/tab_velocity_to_lift.png")

    mw.tab4_subtab1_sub_tabview.set(zh["tab4_subtab1_subtab_4"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "4_toolbox_analysis/resources/tab_curve_to_formula.png")

    # 4.2 加工误差
    mw.tab4_sub_tabview.set(zh["tab4_subtab_2"])
    root.update()
    time.sleep(0.1)
    mw.tab4_subtab2_sub_tabview.set(zh["tab4_subtab2_subtab_1"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "5_toolbox_error/resources/tab_error_correction.png")

    mw.tab4_subtab2_sub_tabview.set(zh["tab4_subtab2_subtab_2"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "5_toolbox_error/resources/tab_diameter_error.png")

    mw.tab4_subtab2_sub_tabview.set(zh["tab4_subtab2_subtab_3"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "5_toolbox_error/resources/tab_error_overlay.png")

    mw.tab4_subtab2_sub_tabview.set(zh["tab4_subtab2_subtab_4"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "5_toolbox_error/resources/tab_error_compare.png")

    # 4.3 DXF 处理
    mw.tab4_sub_tabview.set(zh["tab4_subtab_3"])
    root.update()
    time.sleep(0.1)
    mw.tab4_subtab3_sub_tabview.set(zh["tab4_subtab3_subtab_1"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "6_toolbox_dxf/resources/tab_dxf_compare.png")

    mw.tab4_subtab3_sub_tabview.set(zh["tab4_subtab3_subtab_2"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "6_toolbox_dxf/resources/tab_dxf_discretize.png")

    mw.tab4_subtab3_sub_tabview.set(zh["tab4_subtab3_subtab_3"])
    root.update(); time.sleep(0.15); root.update()
    capture(hwnd, "6_toolbox_dxf/resources/tab_dxf_fit_arc.png")

def snap_login_and_register():
    zh = mw.current_language

    # 1. 登录窗口三通道
    def run_login(self):
        hwnd = self.winfo_id()
        # 硬件ID
        mw.tabview_login.set(zh["login_tabview_2"])
        self.update(); time.sleep(0.2); self.update()
        capture(hwnd, "1_getting_started/resources/login_hardware.png")

        # 账户登录
        mw.tabview_login.set(zh["login_tabview_1"])
        if hasattr(mw, 'username_entry') and mw.username_entry:
            mw.username_entry.delete(0, tk.END)
            mw.username_entry.insert(0, "CamOperator")
        if hasattr(mw, 'password_entry') and mw.password_entry:
            mw.password_entry.delete(0, tk.END)
            mw.password_entry.insert(0, "••••••••••••")
        self.update(); time.sleep(0.2); self.update()
        capture(hwnd, "1_getting_started/resources/login_account.png")

        # 加密狗登录
        mw.tabview_login.set(zh["login_tabview_3"])
        self.update(); time.sleep(0.2); self.update()
        capture(hwnd, "1_getting_started/resources/login_dongle.png")
        self.destroy()

    ctk.CTk.mainloop = run_login
    mw.main()

    # 2. 注册窗口
    def run_reg(self):
        hwnd = self.winfo_id()
        if hasattr(mw, 'register_username_entry') and mw.register_username_entry:
            mw.register_username_entry.delete(0, tk.END)
            mw.register_username_entry.insert(0, "CamOperator")
        if hasattr(mw, 'register_password_entry') and mw.register_password_entry:
            mw.register_password_entry.delete(0, tk.END)
            mw.register_password_entry.insert(0, "••••••••••••")
        if hasattr(mw, 'register_confirm_password_entry') and mw.register_confirm_password_entry:
            mw.register_confirm_password_entry.delete(0, tk.END)
            mw.register_confirm_password_entry.insert(0, "••••••••••••")
        if hasattr(mw, 'register_code_entry') and mw.register_code_entry:
            mw.register_code_entry.delete(0, tk.END)
            mw.register_code_entry.insert(0, "CG-PRO-2026-X892")
        self.update(); time.sleep(0.2); self.update()
        capture(hwnd, "1_getting_started/resources/register_window.png")
        self.destroy()

    ctk.CTk.mainloop = run_reg
    mw.show_register_window()

def snap_parts_library_and_changelog_and_alarm(root):
    zh = mw.current_language

    # 1. 更新日志窗口
    from library.changelog_view import show_changelog_window
    import library.messagebox_view as mbv
    
    def changelog_wait(top):
        top.update(); top.update_idletasks(); time.sleep(0.4); top.update()
        capture(top.winfo_id(), "1_getting_started/resources/changelog_window.png")
        top.destroy()

    orig_wait = ctk.CTkToplevel.wait_window
    ctk.CTkToplevel.wait_window = changelog_wait
    show_changelog_window(root, zh, mw.FONT, mw.center_window)
    ctk.CTkToplevel.wait_window = orig_wait

    # 2. 报警示例弹窗
    def alarm_wait(top):
        top.update(); top.update_idletasks(); time.sleep(0.3); top.update()
        capture(top.winfo_id(), "9_troubleshooting/resources/alarm_example.png")
        top.destroy()

    ctk.CTkToplevel.wait_window = alarm_wait
    mbv.BaseCTkMessageBox(
        master=root,
        title=zh["invalid_input_title"],
        message=zh["error_message_dia_setting"],
        icon="error",
        current_language=zh,
        font=mw.FONT,
        center_window_func=mw.center_window
    )
    ctk.CTkToplevel.wait_window = orig_wait

    # 3. 零件库管理窗口
    from library.parts_library_view import PartsLibraryWindow
    def parts_wait(top):
        top.update(); top.update_idletasks(); time.sleep(0.3); top.update()
        capture(top.winfo_id(), "7_parts_library/resources/parts_library_window.png")
        top.destroy()

    ctk.CTkToplevel.wait_window = parts_wait
    mw.launch_parts_library()
    ctk.CTkToplevel.wait_window = orig_wait

def main():
    print("=== 开始捕获全部高品质真实 UI 截图 ===", flush=True)

    # 步骤 1: 登录 & 注册
    print("\n[Step 1] 捕获登录三通道与注册窗口...", flush=True)
    snap_login_and_register()

    # 步骤 2: 主窗口全标签页
    print("\n[Step 2] 捕获主窗口各标签页与子面板（已填满真实工程参数）...", flush=True)
    def run_main(self):
        populate_all_fields()
        self.update(); time.sleep(0.2); self.update()
        snap_main_tabs(self)
        snap_parts_library_and_changelog_and_alarm(self)
        self.destroy()

    ctk.CTk.mainloop = run_main
    mw.show_main_window()
    print("\n=== 全部截图生成完毕 ===", flush=True)

if __name__ == "__main__":
    main()
