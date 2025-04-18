# 升程转凸轮曲线

此工具输入一个升程曲线文件，输出一个凸轮曲线文件。

## 升程曲线文件

输入一个 DXF 格式的升程曲线文件，文件中的曲线数据中的 X 轴表示角度，Y 坐标表示对应角度下的升程量。X 轴坐标必须大于 0。Y 轴坐标一般最小值为 0 表示基圆部分。曲线必须是线性的。

以下是一个典型的升程曲线示例：
![img](resources/lift.jpg)

## DXF 读取精度

DXF 读取精度参数用于设置 DXF 文件的离散精度，定义原始凸轮曲线离散化后相邻离散点之间的最大距离。设置值越小，对凸轮曲线的识别精度越高，建议设置为 0.005mm，即可满足精度要求。

## 基圆半径

设置对应目标凸轮的基圆半径，基圆半径会影响凸轮的尺寸大小。

## 滚子半径

如果输入的升程数据是滚子中心的升程曲线，则必须在此处设置对应测杆滚子半径，才能正确的生成凸轮轨迹。

## 升程方向

设置升程曲线中 X 轴的角度数据是以 X 轴正向为基准，按照顺时针方向还是逆时针方向定义的角度。

对设置为顺时针生成的凸轮曲线和设置逆时针生成的凸轮曲线比较，两者是相对于X轴上下镜像的关系：
![img](resources/lift_direction.jpg)

## X 轴缩放

此参数用于输出的 html 图形中 X 轴坐标进行缩放处理。设置 0.1 则生成的 html X 轴数据会缩小到标准数据的 0.1 倍。

主要为了方便观察部分升程过小的曲线。

## DXF 保存地址

定义输出的凸轮曲线的文件路径。
