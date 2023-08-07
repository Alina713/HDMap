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
    print(tmp.isValid())
    RC_id = tmp.GetFieldAsInteger64('RC_id')
    left_border_id = tmp.GetFieldAsInteger64('LeftLB_id')
    right_border_id = tmp.GetFieldAsInteger64('RightLB_id')
    LC_seq = tmp.GetFieldAsInteger64('LC_seq')
    print('RC_id: ', RC_id)
    print('LeftLB_id: ', left_border_id)
    print('RightLB_id: ', right_border_id)
    print('LC_seq: ', LC_seq)

     # 路口信息，Sec_outer为前方路口信息
    Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
    Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
    print('Sec_inter: ', Sec_inter)
    print('Sec_outer: ', Sec_outer)

    # 车道所在道路的具体信息
    tmp = a.getFeatureByUid('Road_centerline', RC_id)
    print(tmp.isValid())
    lane_num = tmp.GetFieldAsInteger64('Lane_num')
    print('Lane_num: ', lane_num)
    geo = tmp.GetGeometryRef()
    print("Dimension and name: ", geo.getCoordinateDimension(), geo.getGeometryName())
    assert geo.getGeometryName() == 'LINESTRING'
    geo = hd_map.OGRLineString(geo)
    for i in geo.getPoints():
        print(i.getX(), i.getY(), i.getZ())

    # 信号灯信息
    LC_id0 = str(LC_id)
    # tmp = a.getFeatureByFieldValue('Traffic_light', 'Efflane_id', LC_id0)
    tmp = a.TL_getFeatureByLCid('Traffic_light', 'Efflane_id', LC_id0)
    print(tmp.isValid())
    traffic_id = tmp.GetFieldAsInteger64('Uid')
    print('Traffic_id: ', traffic_id)
    return 0

LC_id2all(14026440)

def LC2intersection(LC_id):
    tmp = a.getFeatureByUid('Lane_centerline', LC_id)
    print(tmp.isValid())
    Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
    Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
    return 0

def Point2LC_id(X, Y, Z):
    tp = a.get_closest_lCid_by_point(X, Y, Z)
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

# LC = Point2LC_id(396800.477202547714114, 3418392.700545833911747, 15.864680063119482)
# LC_id2all(LC)


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