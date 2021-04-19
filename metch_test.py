import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

img1 = cv2.imread('skill1.png',0)
img2 = cv2.imread('sc.png',0)

# 使用SIFT检测角点
sift = cv2.xfeatures2d.SIFT_create()
# 获取关键点和描述符
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# 定义FLANN匹配器
index_params = dict(algorithm = 1, trees = 5)
search_params = dict(checks = 50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
# 使用KNN算法匹配
matches = flann.knnMatch(des1,des2,k=2)

# 去除错误匹配
good = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good.append(m)

# 单应性
if len(good)>MIN_MATCH_COUNT:
    # 改变数组的表现形式，不改变数据内容，数据内容是每个关键点的坐标位置
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    # findHomography 函数是计算变换矩阵
    # 参数cv2.RANSAC是使用RANSAC算法寻找一个最佳单应性矩阵H，即返回值M
    # 返回值：M 为变换矩阵，mask是掩模
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    # ravel方法将数据降维处理，最后并转换成列表格式
    matchesMask = mask.ravel().tolist()
    # 获取img1的图像尺寸
    h,w = img1.shape
    # pts是图像img1的四个顶点
    pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    # 计算变换后的四个顶点坐标位置
    dst = cv2.perspectiveTransform(pts,M)

    # 根据四个顶点坐标位置在img2图像画出变换后的边框
    img2 = cv2.polylines(img2,[np.int32(dst)],True,(255,0,0),3, cv2.LINE_AA)

else:
    print("Not enough matches are found - %d/%d") % (len(good),MIN_MATCH_COUNT)
    matchesMask = None

# 显示匹配结果
draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = (255,0,0),
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
plt.imshow(img3,'gray'),plt.show()
print(good[1].trainIdx)
print(kp2[good[1].trainIdx].pt)

# point2f pt;//位置坐标
# float size; // 特征点邻域直径
# float angle; // 特征点的方向，值为[零, 三百六十)，负值表示不使用
# float response;//最佳匹配
# int octave; // 特征点所在的图像金字塔的组
# int class_id; // 用于聚类的id
# DMatch.distance - 描述符之间的距离。越小越好。
# DMatch.trainIdx - 目标图像中描述符的索引。
# DMatch.queryIdx - 查询图像中描述符的索引。
# DMatch.imgIdx - 目标图像的索引。 

# 上面为可以匹配旋转后的图片，下面匹配与原图方向相同
# import numpy as np
# import cv2
# from matplotlib import pyplot as plt

# queryImage = cv2.imread('aa.jpg',0)
# trainingImage = cv2.imread('bb.png',0)

# # 只使用SIFT 或 SURF 检测角点
# sift = cv2.xfeatures2d.SIFT_create()
# # sift = cv2.xfeatures2d.SURF_create(float(4000))
# kp1, des1 = sift.detectAndCompute(queryImage,None)
# kp2, des2 = sift.detectAndCompute(trainingImage,None)

# # 设置FLANN匹配器参数
# # algorithm设置可参考https://docs.opencv.org/3.1.0/dc/d8c/namespacecvflann.html
# indexParams = dict(algorithm=0, trees=5)
# searchParams = dict(checks=50)
# # 定义FLANN匹配器
# flann = cv2.FlannBasedMatcher(indexParams,searchParams)
# # 使用 KNN 算法实现匹配
# matches = flann.knnMatch(des1,des2,k=2)

# # 根据matches生成相同长度的matchesMask列表，列表元素为[0,0]
# matchesMask = [[0,0] for i in range(len(matches))]

# # 去除错误匹配
# for i,(m,n) in enumerate(matches):
#     if m.distance < 0.7*n.distance:
#         matchesMask[i] = [1,0]

# # 将图像显示
# # matchColor是两图的匹配连接线，连接线与matchesMask相关
# # singlePointColor是勾画关键点
# drawParams = dict(matchColor = (0,255,0),
#                    singlePointColor = (255,0,0),
#                    matchesMask = matchesMask,
#                    flags = 0)
# resultImage = cv2.drawMatchesKnn(queryImage,kp1,trainingImage,kp2,matches,None,**drawParams)
# plt.imshow(resultImage,),plt.show()
