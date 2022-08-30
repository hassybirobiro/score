import sys
import numpy
import cv2
import os
import requests
import shutil
import urllib.request
import datetime
import subprocess
import math

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)

def numpy_mat_sort(mat):
    change = True
    while change:
        change = False
        for i in range(len(mat) - 1):
            if mat[i][0][1] > mat[i + 1][0][1]:
                mat[i], mat[i + 1] = mat[i + 1], mat[i].copy()
                change = True

maxlinegap = 5
do_blur = True
same_line_dis = 3
minlinelength = 100

print(maxlinegap)
print(do_blur)
print(same_line_dis)
print(minlinelength)
    #パスのベースを作成
DS = os.sep
BASE_PATH = os.path.dirname(__file__) + DS
    #楽譜画像のパスを生成
scor_img = 'image.png'
    #指定したデータを指定したファイル名で出力
def debug_image(img, imgname = 'result.png'):
        #画像を出力
    cv2.imwrite(imgname, img)
result_img = cv2.imread(scor_img, cv2.IMREAD_COLOR)
    #五線を認識する
scr = cv2.imread(scor_img)
scr_gray = cv2.cvtColor(scr, cv2.COLOR_RGB2GRAY)
    #途切れてるところがつながるようにぼかしてみる
if do_blur:
    kval = 2
    kernel = numpy.ones((kval,kval),numpy.float32)/(kval*kval)
    scr_gray = cv2.filter2D(scr_gray,-1,kernel)
        #白黒反転
line_dst = cv2.bitwise_not(scr_gray)
    #２値化
retval_line, line_dst = cv2.threshold(line_dst, 30, 255, cv2.THRESH_BINARY)
debug_image(line_dst, 'line_dst.png')
    #線を検出
lines = cv2.HoughLinesP(line_dst, rho=1, theta=numpy.pi/360, threshold=100, minLineLength=minlinelength, maxLineGap=maxlinegap)



dis = 9999
numpy_mat_sort(lines)
dellist = []
for line1 in range(len(lines)):
    for line2 in range(line1, len(lines)):
        if line1 >= len(lines) or line2 >= len(lines):
            break
        if line1 == line2:
            continue
        if min(abs(lines[line1][0][3] - lines[line2][0][3]), abs(lines[line1][0][1] - lines[line2][0][1])) < same_line_dis:
            dellist = dellist + [line2]
lines = numpy.delete(lines, dellist, 0)
print(lines)
print(len(lines))
for line1 in range(len(lines) - 1):
    dis = min(dis, abs(lines[line1][0][3] - lines[line1 + 1][0][3]))
for line in lines:
    x1, y1, x2, y2 = line[0]
            #赤線
    result_img = cv2.line(result_img, (x1, y1), (x2, y2), (0,0,255), 1)
        #五線認識ここまで
        #音符のたま認識
        #楽譜データを読み込む
scr = cv2.imread(scor_img, cv2.IMREAD_COLOR)
        #画像のサイズを取得
height, width, channels = scr.shape
image_size = height * width
        #グレースケール化 ①
scr_filled = cv2.cvtColor(scr, cv2.COLOR_RGB2GRAY)
        #細い線とかをぼかす　ぼかし処理
scr_filled = cv2.bilateralFilter(scr_filled, 15, 140, 10)
        #白黒反転　③
dst = cv2.bitwise_not(scr_filled)
debug_image(dst, 'dst.png')
        #２値化
retval, dst = cv2.threshold(dst, 240, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
debug_image(dst, 'dst2.png')
        #五線の消去
for line in lines:
    x1, y1, x2, y2 = line[0]
    for x in range(x1, x2):
        for y in range(y1, y2):
            pixcel_value_up = scr_filled[y - 2, x]
            pixcel_value_bottom = scr_filled[y + 2, x]
            """if (pixcel_value_up == [0, 0, 0] or pixcel_value_bottom == [0, 0, 0]) and ((scr_filled[y - 2, x - 2] == [0, 0, 0] and scr_filled[y - 2, x + 2] == [0, 0, 0]) or (scr_filled[y + 2, x - 2] == [0, 0, 0] and scr_filled[y + 2, x + 2] == [0, 0, 0])):
                continue"""
                #白線
            dst = cv2.line(dst, (x - 3, y - 1), (x + 3, y + 1), (255,255,255), 1)
debug_image(dst, 'dst_deletedlines.png')
        #輪郭を抽出
cnt, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #抽出した領域を出力 抽出した領域に境界線を引いた画像を出力
dst = cv2.imread(scor_img, cv2.IMREAD_COLOR)
dst = cv2.drawContours(dst, cnt, -1, (0, 0, 255, 255), 2, cv2.LINE_AA)
debug_image(dst, 'dst3.png')
        #認識させるサイズを指定する

minsize = dis ** 2 - 6
print(minsize)
        #20→100→500
maxsize = minsize + 30
print(maxsize)
        #元元3000とか
        #大きいor小さい領域は削除
notes = []
for i, count in enumerate(cnt):
            #小さい領域の場合は無視
    area = cv2.contourArea(count)
    if area < 100:
        continue
            #最大値の指定を追加
    if area > 1000:
        continue
            #画像全体を占める領域を除外
    if 1000 < area:
        continue
            #囲う線を描画する
    x,y,w,h = cv2.boundingRect(count)
    if h >= w * 2 or w >= h * 2:
        continue
    if y < lines[0][0][1]:
        continue
    result_img = cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
    notes.append([x + w / 2, y + h / 2])
        #音符認識ここまで
    #検出結果を表示
debug_image(result_img, 'result.png')
print(notes)
