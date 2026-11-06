# 误差诊断与补偿概览

在精密凸轮高速外圆磨削中，受到机床几何几何误差、砂轮弹性变形与磨损、热伸长、从动机构受力挠曲以及测头对刀偏差等多种物理因素影响，首次试磨工件的实测轮廓往往与设计图纸存在微米级偏差。

**Cam Grinding** 提供了全生命周期的“加工误差”诊断与闭环补偿工具箱，支持**多轮迭代闭环修正**、**砂轮直径偏离敏感度分析**、**测量误差空间叠加**以及**双凸轮几何偏差高保真对比**。

---

## 1. 误差处理工具矩阵

| 工具模块 | 核心功能 | 输入要素 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **[加工误差修正](error_correction.md)** | 三轮廓闭环迭代补偿 | 标准图纸 DXF + 加工用 DXF + 现场实测数据 | 首件试磨不合格后的精密闭环反求修调 |
| **[直径误差分析](diameter_error_analysis.md)** | 砂轮名义/实际直径偏差仿真 | 标准 DXF + 标准砂轮直径 + 实际砂轮直径 | 探究砂轮修整变小对轮廓形状产生的理论畸变 |
| **[CAM 误差叠加](cam_error_superposition.md)** | 空间测量偏差法向/径向叠加 | 基础凸轮 DXF + 偏差离散点表 | 预置非对称补偿、仿真工况变形回贴 |
| **[CAM 误差对比](cam_error_comparison.md)** | 双曲线法向与径向残差统计 | 基准凸轮 1 + 对比凸轮 2 | 工件修调前后比对、加工一致性评估 |

---

## 2. 闭环磨削修调流程（Closed-loop Machining）

```text
[工艺工程师] ──(1. 导入理论标准图纸 Standard.dxf)──> [Cam Grinding]
                                                       │
                                     (2. 导出加工程序与 Program_V1.dxf)
                                                       ▼
[首件试磨加工完成] <──────────(3. 加工磨削)─────────── [数控磨床 CNC]
       │
 (4. 装夹测量)
       ▼
[凸轮测量中心 P65/三坐标] ──(5. 导出实测误差文件 Measured.txt)──> [Cam Grinding]
                                                               │
                                       (6. 计算偏差向量 Δ = Standard - Measured)
                                       (7. 反求生成修正程序 Program_V2)
                                                               ▼
[终测复核合格 ≤ 0.003mm] <──(9. 二次复磨)── [数控磨床] <──(8. 下发修正程序)
```

---

## 3. 误差修正核心数学模型

软件采用三维闭环矢量叠加修正模型：

$$\vec{P}_{\text{new\_program}}(\theta) = \vec{P}_{\text{current\_program}}(\theta) + \alpha \cdot \Big( \vec{P}_{\text{standard}}(\theta) - \vec{P}_{\text{measured}}(\theta) \Big) + \vec{\delta}_{\text{offset}}$$

* $\vec{P}_{\text{standard}}$：图纸理论标准几何模型；
* $\vec{P}_{\text{current\_program}}$：当前实际使用的数控加工凸轮模型；
* $\vec{P}_{\text{measured}}$：测量机实测工件几何模型；
* $\alpha$：阻尼补偿因子（默认取 1.0）；
* $\vec{\delta}_{\text{offset}}$：原点偏移与刚体旋转修正量。
