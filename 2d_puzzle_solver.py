import amplify
from amplify.client import FixstarsClient
import numpy as np

client = FixstarsClient()
client.token = "oa9j6nKrhJn4DR4socoEjc7yXIng2Mz7"
client.parameters.timeout = 1000

def InputShape(shape_list): #図形の入力
    while True:
        tmp_list = list(input())
        if tmp_list != []: shape_list.append(tmp_list)
        else: break

def ConvertToBinaryNdarray(shape_list, row, column): #'.'を0, 'o'を1に変える
    for ri in range(row): 
        for ci in range(column):
            if shape_list[ri][ci] == '.' : 
                shape_list[ri][ci] = 0
            elif shape_list[ri][ci] == 'o' : 
                shape_list[ri][ci] = 1
            else: #違う文字が入っていたら終了
                print("無効な文字が入力されています!")
                exit()

def isZero(shape_ndarray):
    if (np.all(shape_ndarray == 0)): #全て0なら終了
        print("図形が存在しません!")
        exit()

def ShapingNdarray(ndarray): #外側の0しかない行, 列を削除
    while True:
        if np.all(ndarray[0] == 0):
            ndarray = np.delete(ndarray, 0, axis=0)
            print(ndarray)
        else:
            break
    while True:
        if np.all(ndarray[:, 0] == 0):
            ndarray = np.delete(ndarray, 0, axis=1)
            print(ndarray)
        else:
            break
    while True:
        if np.all(ndarray[-1] == 0):
            ndarray = np.delete(ndarray, -1, axis=0)
            print(ndarray)
        else:
            break
    while True:
        if np.all(ndarray[:, -1] == 0):
            ndarray = np.delete(ndarray, -1, axis=1)
            print(ndarray)
        else:
            break
    return ndarray

def OnePosIntoSet(array, m, n): #平行移動したタイルが目的の図形上でどの位置のインデックスにあるかを格納
    tmp_set = set()
    for i in range(len(array[0])):
        tmp_set.add((array[0][i] + m, array[1][i] + n))
    return frozenset(tmp_set) #setのsetは作れないのでfrozensetのsetを作る(中の要素を変更することはないので大丈夫)
    

print("空白のマスを\".\", 目的の図形のマスを\"o\"として、\n全体が長方形のマス目になるように作りたい図形を入力してください\n空行で入力を終了します")
goal_shape = []
InputShape(goal_shape)
ConvertToBinaryNdarray(goal_shape, len(goal_shape), len(goal_shape[0]))
goal_shape = np.array(goal_shape)
isZero(goal_shape)
goal_shape = ShapingNdarray(goal_shape)
goal_one_index_array = np.where(goal_shape == 1)
goal_one_index_set = OnePosIntoSet(goal_one_index_array, 0, 0)
row_size = len(goal_shape)
column_size = len(goal_shape[0])

tile_info = []
loop_count = 0
while True:
    print(f"{loop_count+1}種類目のタイルの数を入力してください\n0で入力を終了します")
    while True:
        try:
            tile_count = int(input())
        except ValueError as e:
            print("数字を入力してください!")
        else:
            break
    if tile_count != 0: tile_info.append([tile_count]) #同じ種類のタイルを何枚使うか
    else: break
    print(f"空白のマスを\".\", タイルのマスを\"o\"として、\n全体が長方形のマス目になるように{loop_count+1}種類目のタイルの形を入力してください")
    tile_shape = []  #タイルの形
    InputShape(tile_shape)
    ConvertToBinaryNdarray(tile_shape, len(tile_shape), len(tile_shape[0]))
    tile_shape = np.array(tile_shape)
    isZero(tile_shape)
    tile_shape = ShapingNdarray(tile_shape)
    tile_info[loop_count].append(len(tile_shape)) #タイルの縦の長さ
    tile_info[loop_count].append(len(tile_shape[0])) #タイルの横の長さ
    tile_info[loop_count].append(tile_shape) #タイルの形
    loop_count += 1
#tile_info: [0]→同じ種類のタイルを何枚使うか　[1]→タイルの縦の長さ　[2]→タイルの横の長さ　[3]→タイルの形


can_rotate = False
can_flip = False
if input("回転を認めますか？(y/n): ") == 'y':
    can_rotate = True
    if input("裏返しを認めますか？(y/n): ") == 'y':
        can_flip = True
if can_rotate and can_flip: #探索の際のforループの回数を決める
    f = 8
elif can_rotate:
    f = 4
else:
    f = 1

q_count = 0 #使用するqubitの数を数える
q_by_tile = [] #それぞれの種類のタイルがどのqubitを使っているかを格納
q_by_index = [[set() for i in range(column_size)] for j in range(row_size)] #目的の図形のマス一つ一つについて、その上に乗るタイルのqubitを格納
for i in range(len(tile_info)):
    can_place_set = set() #目的の図形に重なるようなタイルのindexのfrozensetを格納するためのset
    q_by_tile.append(q_count)
    for fi in range(f): #fiの値によって何回90度回転させるか、裏返すかが決まる
        tmp_tile_list = np.rot90(tile_info[i][3], fi%4)
        if fi//4 == 1: 
            tmp_tile_list = np.transpose(tmp_tile_list)
        tile_one_index_array = np.where(tmp_tile_list == 1)
        #目的の図形上をくまなく平行移動させてタイルを置けるかどうかチェック
        for j in range(row_size - tile_info[i][(fi%4 + fi//4)%2+1]+1): #回転させたり裏返したりすると縦と横の長さが入れ替わるのでそれをfiの値によってうまく分けている
            for k in range(column_size - tile_info[i][(fi%4 + fi//4 + 1)%2+1]+1):
                tmp_tile_set = OnePosIntoSet(tile_one_index_array, j, k) 
                if tmp_tile_set not in can_place_set:
                    can_place_set.add(tmp_tile_set)
                else:
                    continue #置けることが既に分かっているなら新たにqubitを追加する必要がない(タイルの対称性の除去)
                if tmp_tile_set <= goal_one_index_set: #タイルのindexが目的の図形のindexの部分集合であるかを判定
                    for l in tmp_tile_set:
                        q_by_index[l[0]][l[1]].add(q_count)
                    q_count += 1
q_by_tile.append(q_count)

q = amplify.gen_symbols(amplify.BinaryPoly, q_count)
constraints = 0
for i in range(len(tile_info)):
    if q_by_tile[i] == q_by_tile[i+1]: continue
    constraints += amplify.constraint.equal_to(amplify.sum_poly(q[q_by_tile[i]:q_by_tile[i+1]]), tile_info[i][0])
for i in range(row_size):
    for j in range(column_size):
        if q_by_index[i][j] == set(): continue
        constraints += amplify.constraint.equal_to(amplify.sum_poly([q[k] for k in q_by_index[i][j]]), 1)

solver = amplify.Solver(client)
result = solver.solve(constraints)

# 結果を表示
if len(result) == 0:
    raise RuntimeError("Any one of constraints is not satisfied.")
values = result[0].values
q_values = amplify.decode_solution(q, values)
answer = set(np.where(np.array(q_values) == 1)[0])
digit = len(str(max(answer)))
for i in range(row_size):
    for j in range(column_size):
        if q_by_index[i][j] == set():
            print(f"{'*':>{digit}}", end=' ')
        else:
            seki = q_by_index[i][j] & answer
            if len(seki) == 1:
                print(f"{[_ for _ in seki][0]:>{digit}}", end=' ')
            else:
                print(f"{'o':>{digit}}", end=' ')
    print('')