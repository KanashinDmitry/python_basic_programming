import numpy as np
import cv2 as cv

img = {}
img['orig'] = cv.imread('lion.jpg', cv.IMREAD_COLOR)

height, width, channels = img['orig'].shape

img_lower_x2 = cv.resize(img['orig'], (width // 2 + width % 2, height // 2 + height % 2), interpolation=cv.INTER_AREA)

img_lower_x4 = cv.resize(img['orig'], None, fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)

kernel = np.ones((5, 5), np.float32) / 25
kernel_clear = np.ones((3, 3), np.float32) * (-1)
kernel_clear[1, 1]=9;

img['canny'] = cv.Canny(img_lower_x2, 100, 200)
img['canny'] = cv.cvtColor(img['canny'], cv.COLOR_GRAY2BGR) 
img['avg'] = cv.filter2D(img_lower_x4, -1, kernel) #cv.blur(img, (5, 5))
img['gauss'] = cv.GaussianBlur(img_lower_x4, (5,5), 0)
img['clear'] = cv.filter2D(img_lower_x4, -1, kernel_clear)
img['rand'] = np.random.randint(255, size=img_lower_x4.shape, dtype=np.uint8)

half_height = height // 2 + height % 2
quarter_height = height // 4
quarter_width = width // 4

res = np.zeros((height, width + width // 2, channels), dtype=np.uint8)
res[0:height, 0:width] = img['orig']
res[0:half_height, width:] = img['canny']
res[half_height:half_height + quarter_height, width:width + quarter_width] = img['avg']
res[half_height:half_height + quarter_height, width + quarter_width:] = img['gauss']
res[half_height + quarter_height:, width:width + quarter_width] = img['clear']
res[half_height + quarter_height:, width + quarter_width:] = img['rand']

cv.imwrite('result.jpg', res)
