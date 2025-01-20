# TRANSMIT

**TRANSMIT**功能需要使用**TRANSMIT 和柱面转换**选件，该选件需授权。

此功能可以将直线轴和旋转轴转换到直角坐标系中编程，方便的实现凸轮/立方体的加工。

**语法：**
```
TRANSMIT: 激活含第一个 TRANSMIT 数据组的 TRANSMIT 功能
TRANSMIT(n): 激活含第 n 个 TRANSMIT 数据组的 TRANSMIT 功能
TRAFOOF: 取消转换
```

**每个通道可以设置两个 transmit 转换。** 如果没有指定具体数据组，默认调用第一个数据组。

使用此功能需要配置**通用机床数据**和**通道机床数据**，下面通过示例来说明配置过程：

首先在通用机床数据中定义设备可用的轴：
```
MD10000[0] $MN_AXCONF_MACHAX_NAME_TAB X1  #垂直于旋转轴的直线轴
MD10000[1] $MN_AXCONF_MACHAX_NAME_TAB Z1  #平行于旋转轴的直线轴
MD10000[2] $MN_AXCONF_MACHAX_NAME_TAB C1  #旋转轴
MD10000[3] $MN_AXCONF_MACHAX_NAME_TAB V1
MD10000[4] $MN_AXCONF_MACHAX_NAME_TAB W1
```

配置 C1 轴为旋转轴：
```
MD30300 $MA_IS_ROT_AX[2] 1
MD30310 $MA_ROT_IS_MODULO[2] 1 
MD30320 $MA_DISPLAY_IS_MODULO[2] 1
```

然后再通道机床数据配置：
```
通道轴名称不能和机床轴名称一样
MD20080[0] $MC_AXCONF_CHANAX_NAME_TAB X
MD20080[1] $MC_AXCONF_CHANAX_NAME_TAB Z
MD20080[2] $MC_AXCONF_CHANAX_NAME_TAB C
MD20080[3] $MC_AXCONF_CHANAX_NAME_TAB V
MD20080[4] $MC_AXCONF_CHANAX_NAME_TAB W

通道轴和机床轴的对应关系，顺序和 20080 一致，编号是机床轴编号 如 1 表示机床轴 X1
MD20070[0] $$MC_AXCONF_MACHAX_USED 1  #将 X 和 X1 绑定
MD20070[1] $$MC_AXCONF_MACHAX_USED 2
MD20070[2] $$MC_AXCONF_MACHAX_USED 3
MD20070[3] $$MC_AXCONF_MACHAX_USED 4
MD20070[4] $$MC_AXCONF_MACHAX_USED 5
```

定义几何轴名称：
```
MD20060[0] $MC_AXCONF_GEOAX_NAME_TAB X  #几何轴名称 可以和通道轴名称不一样
MD20060[1] $MC_AXCONF_GEOAX_NAME_TAB Y
MD20060[2] $MC_AXCONF_GEOAX_NAME_TAB Z
```

未激活 transmit 时的几何轴分配：
```
MD20050[0] $MC_AXCONF_GEOAX_ASSIGN_TAB 1  #通道轴 1，也就是 X
MD20050[1] $MC_AXCONF_GEOAX_ASSIGN_TAB 0  #不分配通道轴
MD20050[2] $MC_AXCONF_GEOAX_ASSIGN_TAB 2  #通道轴 2，也就是 Z

以上配置在通用情况下将 X Z 轴分配给第 1 3 几何轴
```

激活 transmit 数据组 1 时的几何轴分配：
```
MD24120[0] $MC_TRAFO_GEOAX_ASSIGN_TAB_1 1  #通道轴 1，也就是 X
MD24120[1] $MC_TRAFO_GEOAX_ASSIGN_TAB_1 3  #通道轴 3，也就是 C
MD24120[2] $MC_TRAFO_GEOAX_ASSIGN_TAB_1 2  #通道轴 2，也就是 Z

MD24100    $MC_TRAFO_TYPE_1    256   #一根回转轴和一根直线轴，257 为两个直线轴
MD24110[0] $MC_TRAFO_AXES_IN_1 1     #定义垂直于回转轴的直线轴，此处设置 1 表示 X 轴
MD24110[1] $MC_TRAFO_AXES_IN_1 3     #定义回转轴，此处设置 3 表示 C 轴
MD24110[2] $MC_TRAFO_AXES_IN_1 2     #定义平行于回转轴的直线轴，此处设置 2 表示 Z 轴

以上配置在激活 transmit 情况下将 X C Z 轴分配给第 1 2 3 几何轴
激活后会虚拟出一个 Y 轴，构成 X Y Z 几何轴
```

### 注意事项

**transmit** 启动后运行在 **G53** 状态下，会抑制可设定零点偏移和可编程零点偏移，所有 **G54/TRANS** 等零点偏移指令无法正常运行，如果在进行坐标转换时需要对 X 或 C 轴进行坐标偏移，只能通过设置**回转轴偏移: TRANSMIT_ROT_AX_OFFSET**和**刀具零点位置: TRANSMIT_BASE_TOOL**实现。注意这两个参数都是 **cf** 有效，即必须点**机床数据有效**才会生效。如果要在 nc 程序中动态设置，需要在设置后执行 **NEWCONF** 指令。

下面是一个设置示例：
```
24900    $MC_TRANSMIT_ROT_AX_OFFSET_1 60  #将回转轴偏移到 60 度处
24920[0] $MC_TRANSMIT_BASE_TOOL_1 -10     #将 数据组 1 第一几何轴偏移到 -10 处
24920[1] $MC_TRANSMIT_BASE_TOOL_1 0
24920[2] $MC_TRANSMIT_BASE_TOOL_1 0
```

下面是一个激活 transmit 并进行圆弧插补运动的示例代码：
```
G90 G0 X5 Z0 C60  ;运动到起始位置

$MC_TRANSMIT_BASE_TOOL_1[0]=-10 ;设置 X 轴偏移
$MC_TRANSMIT_ROT_AX_OFFSET_1=60 ;设置 C 轴偏移
NEWCONF ;机床数据有效

TRANSMIT ;激活坐标转换

G01 X=15.0000 Y=0.0000
G01 X=15.0000 Y=0.0000
G02 X=6.0057 Y=-14.2777 CR=33.4671

TRAFOOF ;关闭坐标转换

M30
```
