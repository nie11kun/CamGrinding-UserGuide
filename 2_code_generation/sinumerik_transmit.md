# 西门子 SINUMERIK 机床配置

在数控凸轮磨床上加工非圆轮廓时，数控系统通常通过 **极坐标转换（TRANSMIT）** 或 **多轴联动点位插补** 实现砂轮架进给轴（`X`）与工件旋转主轴（`C`）的高动态协同。

---

## 1. TRANSMIT 极坐标转换概述

**TRANSMIT（Transmit and Cylinder Surface Transformation）** 是西门子 SINUMERIK 系统的高级运动学转换选件：
* **核心功能**：将机床的直线进给轴（通常为 `X` 轴）和回转分度轴（通常为 `C` 轴）虚拟投影为笛卡尔直角坐标系中的第一与第二几何轴（`X-Y`）。
* **编程优势**：零件轮廓可以直接以图纸笛卡尔坐标（`X/Y`）配合标准直线（`G01`）与圆弧（`G02/G03`）进行插补，由数控内核实时解算非线性逆运动学。
* **选件要求**：使用该功能需机床已开通“TRANSMIT 和柱面转换”软件授权选件。

```
TRANSMIT        ; 激活第 1 个 TRANSMIT 转换数据组
TRANSMIT(n)     ; 激活第 n 个 TRANSMIT 转换数据组（每个通道最多支持 2 组）
TRAFOOF         ; 关闭所有坐标转换，恢复物理机床坐标轴控制
```

---

## 2. 机床数据配置体系

在西门子 840D / 840D sl / ONE 系统中，启用 TRANSMIT 需按顺序配置通用机床数据、轴数据和通道数据。

### 2.1 通用机床数据（MD10000）

定义数控系统底层物理轴名称：

```ini
; 物理机床轴定义
MD10000[0] MN_AXCONF_MACHAX_NAME_TAB[0] = "X1"  ; 垂直于工件回转轴的砂轮进给直线轴
MD10000[1] MN_AXCONF_MACHAX_NAME_TAB[1] = "Z1"  ; 平行于工件回转轴的轴向移动直线轴
MD10000[2] MN_AXCONF_MACHAX_NAME_TAB[2] = "C1"  ; 工件头架高精度回转主轴
MD10000[3] MN_AXCONF_MACHAX_NAME_TAB[3] = "V1"  ; 砂轮修整器进给轴（可选）
MD10000[4] MN_AXCONF_MACHAX_NAME_TAB[4] = "W1"  ; 砂轮修整器横移轴（可选）
```

### 2.2 回转轴专用数据（MD30000 系列）

确保工件头架 `C` 轴作为旋转模态轴正确运行：

```ini
MD30300 MA_IS_ROT_AX[2] = 1        ; 设置第 3 轴（C1）为旋转轴
MD30310 MA_ROT_IS_MODULO[2] = 1    ; 启用模态回转分度（0° ~ 360° 循环）
MD30320 MA_DISPLAY_IS_MODULO[2] = 1 ; 界面模态显示角度
```

### 2.3 通道机床数据（MD20000 系列）

绑定通道轴并定义几何轴分配：

```ini
; 1. 通道轴名称定义（不可与机床物理轴重名）
MD20080[0] MC_AXCONF_CHANAX_NAME_TAB[0] = "X"
MD20080[1] MC_AXCONF_CHANAX_NAME_TAB[1] = "Z"
MD20080[2] MC_AXCONF_CHANAX_NAME_TAB[2] = "C"

; 2. 通道轴与机床物理轴编号绑定（1:X1, 2:Z1, 3:C1）
MD20070[0] MC_AXCONF_MACHAX_USED[0] = 1
MD20070[1] MC_AXCONF_MACHAX_USED[1] = 2
MD20070[2] MC_AXCONF_MACHAX_USED[2] = 3

; 3. 几何轴名称定义
MD20060[0] MC_AXCONF_GEOAX_NAME_TAB[0] = "X"
MD20060[1] MC_AXCONF_GEOAX_NAME_TAB[1] = "Y"  ; 虚拟几何轴
MD20060[2] MC_AXCONF_GEOAX_NAME_TAB[2] = "Z"

; 4. 未激活 TRANSMIT 时的几何轴映射（通道轴 1->X, 2->Z）
MD20050[0] MC_AXCONF_GEOAX_ASSIGN_TAB[0] = 1
MD20050[1] MC_AXCONF_GEOAX_ASSIGN_TAB[0] = 0  ; 不分配通道轴
MD20050[2] MC_AXCONF_GEOAX_ASSIGN_TAB[2] = 2
```

### 2.4 TRANSMIT 转换数据组配置（MD24100 系列）

激活转换后，数控系统将虚拟出平面 `Y` 轴与 `X` 轴联动：

```ini
MD24100 MC_TRAFO_TYPE_1 = 256              ; 256 表示 1 根回转轴 + 1 根直线轴转换
MD24110[0] MC_TRAFO_AXES_IN_1[0] = 1       ; 垂直于回转轴的直线轴（通道轴 1: X）
MD24110[1] MC_TRAFO_AXES_IN_1[1] = 3       ; 回转轴（通道轴 3: C）
MD24110[2] MC_TRAFO_AXES_IN_1[2] = 2       ; 平行于回转轴的直线轴（通道轴 2: Z）

MD24120[0] MC_TRAFO_GEOAX_ASSIGN_TAB_1[0] = 1 ; 几何轴 X 分配给通道轴 1
MD24120[1] MC_TRAFO_GEOAX_ASSIGN_TAB_1[1] = 3 ; 几何轴 Y 由通道轴 3（C轴）解算生成
MD24120[2] MC_TRAFO_GEOAX_ASSIGN_TAB_1[2] = 2 ; 几何轴 Z 分配给通道轴 2
```

---

## 3. 关键注意事项：零点偏移与动态重构

> [!WARNING]
> **TRANSMIT 激活状态下的零点偏移抑制**
> 
> `TRANSMIT` 启动后系统自动运行在 `G53` 状态下，系统会**强制抑制可设定零点偏移（G54~G59）与可编程零点偏移（TRANS/ATRANS）**。
> 若直接在加工代码中使用 `G54` 或 `TRANS`，其位移将被忽略或引发轨迹异常。

要在 TRANSMIT 模式下实现工件对刀偏移与角度基准相位调整，必须通过专用转换机床数据进行设定：

1. **回转轴相位偏置**：`MC_TRANSMIT_ROT_AX_OFFSET_n`（参数 MD24900）
2. **直线轴刀具偏置**：`MC_TRANSMIT_BASE_TOOL_n`（参数 MD24920）
3. **动态生效机制**：上述参数具有 `cf`（Confirm）属性。若在 NC 程序中动态赋值，**必须紧跟执行 `NEWCONF` 指令**重载生效。

```ini
; TRANSMIT 动态轴偏置参数定义
MD24900 MC_TRANSMIT_ROT_AX_OFFSET_1 = 60.0    ; 数据组 1 回转轴偏移到 60 度处
MD24920[0] MC_TRANSMIT_BASE_TOOL_1[0] = -10.0 ; 数据组 1 第一几何轴偏移到 -10mm 处
MD24920[1] MC_TRANSMIT_BASE_TOOL_1[1] = 0.0
MD24920[2] MC_TRANSMIT_BASE_TOOL_1[2] = 0.0
```

---

## 4. 高速高精磨削插补控制指令

为了保证凸轮外圆轮廓的光顺性、消除机床换向冲击并抑制多边形振纹，推荐在数控代码开头启用西门子先进样条与前瞻控制指令：

| 控制指令 | 功能说明 | 推荐设置 |
| :--- | :--- | :--- |
| `COMPCAD` | 启用高级 CAD 表面压缩器，将短线段重构为光滑多项式样条 | 凸轮精磨必备 |
| `FFWON` | 启用速度/加速度前馈控制，大幅减小跟踪滞后误差 | 开启 |
| `SOFT` | 采用 S 型加速度（Jerk 柔性加减速控制），避免突变冲击 | 开启 |
| `FIFOCTRL` | 开启插补缓冲区预读优化，防止高速加工中欠刀断流 | 推荐开启 |
| `CYCLE832(0.001, 1)` | 调用高速加工循环，设定精加工轮廓公差为 0.001 mm | 精磨段调用 |

---

## 5. 标准加工程序结构范例

以下为 **Cam Grinding** 配套输出的西门子标准精磨程序框架：

```gcode
; ====================================================================
; PROGRAM: CAM_GRIND_FINISH.MPF
; PIECE: SK722-CAM-01
; DATE: 2026-11-06
; ====================================================================
G90 G17 G710 G94          ; 绝对坐标, XY 平面, 公制尺寸, 每分钟进给
G500                      ; 取消基础坐标偏置

; 1. 运动到安全换刀与进给起始点
G00 X150.000 Z20.000 C0.000

; 2. 动态设置 TRANSMIT 旋转与基础偏置
MC_TRANSMIT_BASE_TOOL_1[0] = -12.500   ; X 轴刀具基础偏置
MC_TRANSMIT_ROT_AX_OFFSET_1 = 45.000   ; 凸轮基准相位偏移 45 度
NEWCONF                                ; 动态激活机床数据

; 3. 激活高速高精运动控制
SOFT
FFWON
COMPCAD
CYCLE832(0.001, 1)                     ; 精加工公差 0.001mm

; 4. 激活 TRANSMIT 坐标转换
TRANSMIT

; 5. 快速定位至逼近切入点
G00 X=35.0000 Y=0.0000 Z=-5.000
G01 G41 X=30.0000 Y=0.0000 F800

; 6. 轮廓圆弧与直线插补磨削段
G01 X=28.5000 Y=0.0000 F150
G02 X=18.4215 Y=-12.3340 CR=32.450
G01 X=12.1104 Y=-18.6651
G02 X=-15.3421 Y=-10.2231 CR=24.120
G02 X=-25.0000 Y=0.0000 CR=18.500
; ... [后续轮廓数据由软件自动生成] ...

; 7. 退刀与关闭转换
G40 G01 X=35.0000 Y=0.0000 F1000
TRAFOOF                                ; 关闭 TRANSMIT 转换

; 8. 复位与程序结束
G00 X150.000 Z50.000
M30
```
