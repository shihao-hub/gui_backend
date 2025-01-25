import numpy as np

arr = np.array([1, 2, 3, 4, 5])
for e in arr:
    # print(e)
    pass
print("------")

array2d = np.array([[1, 2, 3],
                    [4, 5, 6]])

print(array2d[:, 0])
print(array2d[:, :1])
print("------")

arr84 = np.empty((8, 4))
# for i in range(8):
#     arr84[i] = i
# print(arr84)
print(arr84[[4, 3, 0, 6]])
print(np.arange(8))
print("------")

arr3d = np.array([
    [
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [1, 2, 3],
        [4, 5, 6]
    ]
])
arr = np.arange(24).reshape(2, 3, 4)
print(arr)
print(arr.transpose(1, 0, 2))
