import matplotlib.pyplot as plt
from PIL import Image

img = Image.open(r"E:\桌面\微信图片_20251125183030_269_79.jpg")  # 图片路径
plt.imshow(img)
plt.axis("off")                  # 不显示坐标轴
plt.show()
