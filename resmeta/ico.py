from PIL import Image
img = Image.open('img/icon.png')
img.save('icon.ico', format='ICO', sizes=[(128, 128), (64, 64), (32, 32), (16, 16)])  # 多尺寸兼容
