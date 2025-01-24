"""
### 随笔
1. numpy 是一个强大的科学计算库，它提供了大量的数学函数和工具，可以用于数值计算、线性代数、随机数生成、图像处理等任务。值得学习！

"""

import numpy as np

# NOTE: numpy 应该有很多统计学家等数学相关专业的论文支撑，这些数学公式和算法肯定都是经过验证的。

# 数值计算 -> np.dot
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("Dot product:", np.dot(a, b))

# 线性代数 -> np.linalg.inv
matrix = np.array([[1, 2], [3, 4]])
print("Matrix inverse:\n", np.linalg.inv(matrix))

# 随机数生成 -> np.random.normal, np.mean
random_data = np.random.normal(0, 1, 100)  # 生成 100 个正态分布随机数
print("Mean:", np.mean(random_data))

# 图像处理（假设图像是 2D 数组） -> np.random.randint
image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
cropped_image = image[10:50, 20:60]  # 裁剪图像
