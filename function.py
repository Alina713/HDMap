import hd_map
from osgeo import ogr
# import numpy as np
# from scipy.spatial import KDTree

# 读取涂层
a = hd_map.HDMap()
a.readFromSqlLite('../HDMap/lingang/shp_utm/Traffic_light.shp')
a.readFromSqlLite('../HDMap/lingang/shp_utm/Lane_boundary.shp')
a.readFromSqlLite('../HDMap/lingang/shp_utm/Lane_centerline.shp')
a.readFromSqlLite('../HDMap/lingang/shp_utm/Road_centerline.shp')


# 根据LC_id找到其他信息
def LC_id2all(LC_id):
    # 道路 左右车道边界 道路第几车道
    tmp = a.getFeatureByUid('Lane_centerline', LC_id)
    # print(tmp.isValid())
    RC_id = tmp.GetFieldAsInteger64('RC_id')
    return RC_id
    # left_border_id = tmp.GetFieldAsInteger64('LeftLB_id')
    # right_border_id = tmp.GetFieldAsInteger64('RightLB_id')
    # LC_seq = tmp.GetFieldAsInteger64('LC_seq')
    # print('RC_id: ', RC_id)
    # print('LeftLB_id: ', left_border_id)
    # print('RightLB_id: ', right_border_id)
    # print('LC_seq: ', LC_seq)

     # 路口信息，Sec_outer为前方路口信息
    # Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
    # Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
    # print('Sec_inter: ', Sec_inter)
    # print('Sec_outer: ', Sec_outer)

    # 车道所在道路的具体信息
    # tmp = a.getFeatureByUid('Road_centerline', RC_id)
    # print(tmp.isValid())
    # lane_num = tmp.GetFieldAsInteger64('Lane_num')
    # print('Lane_num: ', lane_num)
    # geo = tmp.GetGeometryRef()
    # print("Dimension and name: ", geo.getCoordinateDimension(), geo.getGeometryName())
    # assert geo.getGeometryName() == 'LINESTRING'
    # geo = hd_map.OGRLineString(geo)
    # for i in geo.getPoints():
    #     print(i.getX(), i.getY(), i.getZ())

    # 信号灯信息
    # LC_id0 = str(LC_id)
    # # tmp = a.getFeatureByFieldValue('Traffic_light', 'Efflane_id', LC_id0)
    # tmp = a.TL_getFeatureByLCid('Traffic_light', 'Efflane_id', LC_id0)
    # print(tmp.isValid())
    # traffic_id = tmp.GetFieldAsInteger64('Uid')
    # print('Traffic_id: ', traffic_id)
    # return 0

# LC_id2all(14026440)

def LC2intersection(LC_id):
    tmp = a.getFeatureByUid('Lane_centerline', LC_id)
    # print(tmp.isValid())
    Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
    Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
    return Sec_outer
    # return 0

def Point2LC_id(X, Y, Z):
    tp = a.get_closest_LCid_by_point(X, Y, Z)
    return tp
    # # P = OGRPoint(X, Y, Z)
    # P = ogr.Geometry(ogr.wkbPoint)
    # P.AddPoint(X, Y, Z)

    # L = a.getLayerByName('Lane_centerline')

    # # 14027481 can be ANY LC_uid
    # v = a.getFeatureByUid('Lane_centerline', 14027481)

    # print(type(P),type(L),type(v))

    # # a.getInitialPoseClosestFeature(P, L, v)
    # # tp = v.GetFieldAsInteger64("Uid")
    # # return tp

def Point2all(X, Y, Z):
    LC_info0 = Point2LC_id(X, Y, Z)
    LC_info = str(LC_info0)
    LC_id2all(LC_info)
    return 0

# LC = Point2LC_id(397600.477202547714114, 3418392.700545833911747, 15.864680063119482)
# print("LC_id:", LC)
# LC_id2all(LC)

def p2l_distance(X, Y, Z, LC_id):
    tmp = a.getFeatureByUid('Lane_centerline', LC_id)
    o = hd_map.OGRPoint(X, Y, Z)
    geo = tmp.GetGeometryRef()
    assert geo.getGeometryName() == 'LINESTRING'
    geo = hd_map.OGRLineString(geo)
    # create ogrlinestring
    line = ogr.Geometry(ogr.wkbLineString)
    for i in geo.getPoints():
        line.AddPoint(i.getX(), i.getY(), i.getZ())

    #create ogrpoint
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(X, Y, Z)

    distance = point.Distance(line)
    # print(distance)
    # name = line.GetGeometryName()
    # length = line.Length()
    # print("The geometry name is:", name)
    # print("The length is:", length)
    return distance

def p2intersection_distance(X, Y, Z, LC_id):
    tmp = a.getFeatureByUid('Lane_centerline', LC_id)
    o = hd_map.OGRPoint(X, Y, Z)
    geo = tmp.GetGeometryRef()
    assert geo.getGeometryName() == 'LINESTRING'
    geo = hd_map.OGRLineString(geo)

    # create ogrlinestring
    line = ogr.Geometry(ogr.wkbLineString)
    for i in geo.getPoints():
        line.AddPoint(i.getX(), i.getY(), i.getZ())

    #create ogrpoint
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(X, Y, Z)

    point2 = ogr.Geometry(ogr.wkbPoint)
    points = geo.getPoints() # get a list of tuples of coordinates
    point2.AddPoint(points[-1].getX(), points[-1].getY(), points[-1].getZ())

    distance = point1.Distance(point2)
    print(distance)
    return 0

def demo(X, Y, Z):
    LC_id = Point2LC_id(X, Y, Z)
    dist = p2l_distance(X, Y, Z, LC_id)
    len = p2intersection_distance(X, Y, Z, LC_id)
    RC_id = LC_id2all(LC_id)
    Section_id = LC2intersection(LC_id)

    print("LC_id: ", LC_id)
    print("dist: ", dist)
    print("len: ", len)
    print("RC_id: ", RC_id)
    print("Section_id: ", Section_id)
    return 0

demo(396952.398740138974972, 3418679.14018150838092, 15.923777061993199)


# p2l_distance(397600.477202547714114, 3418392.700545833911747, 15.864680063119482, 14027488)
p2intersection_distance(396923.251432374177966, 3418728.075290133245289, 15.853474200886486, 14027488)
# # 定义一个函数，输入为点的坐标和直线的方向向量
# def point_to_line_distance_3d(point, vector):
#   # 计算点的坐标
#   x = point[0]
#   y = point[1]
#   z = point[2]

#   # 计算直线的方向向量
#   a = vector[0]
#   b = vector[1]
#   c = vector[2]

#   # 使用点到直线距离公式：d = |(a * x + b * y + c * z) / sqrt(a^2 + b^2 + c^2)|
#   d = abs((a * x + b * y + c * z) / ((a ** 2 + b ** 2 + c ** 2) ** 0.5))

#   # 返回距离
#   return d

# # 测试函数
# point = (1, 2, 3) # 点的坐标
# vector = (4, -5, 6) # 直线的方向向量
# distance = point_to_line_distance_3d(point, vector) # 调用函数
# print(f"The distance from point {point} to line {vector} is {distance:.2f}") # 打印结果


# # 定义一个函数，输入为两点的坐标
# def direction_vector_3d(point1, point2):
#   # 计算两点的坐标
#   x1 = point1[0]
#   y1 = point1[1]
#   z1 = point1[2]
#   x2 = point2[0]
#   y2 = point2[1]
#   z2 = point2[2]

#   # 使用向量减法公式：v = p2 - p1
#   v = (x2 - x1, y2 - y1, z2 - z1)

#   # 返回方向向量
#   return v

# # 测试函数
# point1 = (1, 2, 3) # 第一个点的坐标
# point2 = (4, -5, 6) # 第二个点的坐标
# vector = direction_vector_3d(point1, point2) # 调用函数
# print(f"The direction vector of the line passing through points {point1} and {point2} is {vector}") # 打印结果


# tmp = a.getFeatureByUid('Traffic_light', 2772)
# print(tmp.isValid())
# lane_id = tmp.GetFieldAsInteger64('Efflane_id')
# print('Efflane_id: ', lane_id)
# tmp = a.getFeatureByUid('Lane_centerline', lane_id)
# print(tmp.isValid())
# road_id = tmp.GetFieldAsInteger64('RC_id')
# left_border_id = tmp.GetFieldAsInteger64('LeftLB_id')
# right_border_id = tmp.GetFieldAsInteger64('RightLB_id')
# print('RC_id: ', road_id)
# print('LeftLB_id: ', left_border_id)
# print('RightLB_id: ', right_border_id)
# tmp = a.getFeatureByUid('Road_centerline', road_id)
# lane_num = tmp.GetFieldAsInteger64('Lane_num')
# print('Lane_num: ', lane_num)
# geo = tmp.GetGeometryRef()
# print("Dimension and name: ", geo.getCoordinateDimension(), geo.getGeometryName())
# assert geo.getGeometryName() == 'LINESTRING'
# geo = hd_map.OGRLineString(geo)
# for i in geo.getPoints():
#     print(i.getX(), i.getY(), i.getZ())



# from scipy.spatial import KDTree
# data = [(40.7128, -74.0060), (34.0522, -118.2437), (41.8781, -87.6298), (29.7604, -95.3698), (39.7392, -104.9903)]

# tree = KDTree(data)

# point = (38.9072, -77.0369) # 华盛顿特区 dist, ind = tree.query(point)

# print(f" {point} 的最近邻居是 {data[ind]} ，距离为 {dist:.2f}")

    # tmp = a.getFeatureByUid('Road_centerline', road_id)
    # lane_num = tmp.GetFieldAsInteger64('Lane_num')
    # print('Lane_num: ', lane_num)
    # geo = tmp.GetGeometryRef()
    # print("Dimension and name: ", geo.getCoordinateDimension(), geo.getGeometryName())
    # assert geo.getGeometryName() == 'LINESTRING'
    # geo = hd_map.OGRLineString(geo)
    # for i in geo.getPoints():
    #     print(i.getX(), i.getY(), i.getZ())

# def ogrget(X, Y, Z):
#     OGRPointWrapper(X, Y, Z)
#     return 0