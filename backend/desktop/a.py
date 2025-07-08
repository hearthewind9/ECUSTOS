# 引入必要的库
import matplotlib.pyplot as plt
import numpy as np

# --- 1. 准备数据 ---
# 使用numpy生成一组x坐标数据，从0到2π(约6.28)，共100个点
x = np.linspace(0, 2 * np.pi, 100)
# 计算每个x点对应的正弦值y
y = np.sin(x)

# --- 2. 创建图表 ---
# 创建一个图表窗口，可以指定尺寸
plt.figure(figsize=(10, 6))

# 使用 plot() 函数绘制线图
# 'b-' 表示蓝色(blue)的实线(solid line)
# label 用于在图例中显示
plt.plot(x, y, 'b-', label='y = sin(x)')

# --- 3. 美化图表 ---
# 添加图表标题，并设置中文字体（如果显示乱码）
# 注意：为了正确显示中文，您的系统可能需要有中文字体
plt.title('简单的正弦函数图像 (Sine Wave)')
# 添加X轴标签
plt.xlabel('X 轴 (弧度)')
# 添加Y轴标签
plt.ylabel('Y 轴 (值)')

# 添加网格线，让图表更易读
plt.grid(True)

# 显示图例（会显示每个plot中定义的label）
plt.legend()

# 设置坐标轴范围
plt.xlim(0, 2 * np.pi)
plt.ylim(-1.2, 1.2)

# --- 4. 显示图表 ---
# 调用 show() 函数来显示我们创建的图表窗口
plt.show()

print("图表窗口已关闭。")