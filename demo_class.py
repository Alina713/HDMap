from map import HDMap
import hd_map
from osgeo import ogr
# import gdal
# import ogr
import numpy as np
from tqdm import tqdm
from collections import defaultdict

# 继承map.py中的class HDMap
class HDMapDemo(HDMap):
    # 可修改为anting
    map_name = 'lingang'
    a = hd_map.HDMap()

    def __init__(self):
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Traffic_light.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Lane_boundary.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Lane_centerline.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Road_centerline.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Intersection.shp')

        self.lanecenterlines = {}
        self.lanecenterlineconnectors = {}
        self.laneboundaries = {}
        self.laneboundaryconnectors = {}
        self.intersections = {}
        self.R2LC = {}
        self.RC2LCC = {}
        self.LCCstatus = {}
        self.Traffic_light = {}
        
        # self._get_intersections()
        # self._get_real_lanes()
        # self._get_virtual_lanes()
        # pass

    # set X_info to self.X
    # 返回file_name中对应的涂层个数
    def set_X_info(self, file_name):
        ds = ogr.Open('../HDMap/' + self.map_name +'/shp_utm/'+ file_name +'.shp')
        # 获取第一个图层
        layer = ds.GetLayerByIndex(0)
        # 获取图层中的要素个数
        n = layer.GetFeatureCount()
        # 获取图层中的属性表表头
        defn = layer.GetLayerDefn()
        # 获取属性表字段个数
        m = defn.GetFieldCount()
        # 创建空的数组，根据需要调整维度和数据类型
        array = np.empty((n, m + 1), dtype=object)
        # 遍历图层中的要素
        for i in range(n):
            # 获取第i个要素
            feature = layer.GetFeature(i)
            # 获取要素的几何体，转换为WKT格式
            geometry = feature.GetGeometryRef().ExportToWkt()
            # 将几何体赋值给self数组的第i行第0列
            array[i, 0] = geometry
            # 遍历要素的属性字段
            for j in range(m):
                # 获取第j个字段定义
                field = defn.GetFieldDefn(j)
                # 获取字段名
                name = field.GetNameRef()
                # 获取字段值，根据需要选择字段索引或名称
                value = feature.GetField(name)
                # 将字段值赋值给self数组的第i行第j+1列
                array[i, j + 1] = value

        # 一定记得指定数组！！！！
        if file_name == "Lane_centerline":
            self.lanecenterlines = array
            # print("LC:", self.lanecenterlines[1])
        elif file_name == "Intersection":
            self.intersections = array
            # print("Sec:", self.intersections[1])
        elif file_name == "Traffic_light":
            self.Traffic_light = array
            # print("TLight:", self.Traffic_light[2])
        return n

    def get_data_from_location(self, x, y, z):
        tmp_LC_id = self.a.get_closest_LCid_by_point(x, y, z)
        tmp_dist = self.p2l_distance(x, y, z, tmp_LC_id)
        tmp_len = self.p2intersection_distance(x, y, z, tmp_LC_id)
        tmp_RC_id = self.LC_id2Road_info(tmp_LC_id)
        tmp_sec_id = self.LC2intersection(tmp_LC_id)
        
        res = {}
        res['LC_id'] = tmp_LC_id
        res['dist'] = tmp_dist
        res['len'] = tmp_len
        res['R_id'] = tmp_RC_id
        res['Section_id'] = tmp_sec_id
        return res
    
    # service for get_data_from_location
    def p2l_distance(self, X, Y, Z, LC_id):
        tmp = self.a.getFeatureByUid('Lane_centerline', LC_id)
        # o = hd_map.OGRPoint(X, Y, Z)
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
        return distance
    
    # problem && service for get_data_from_location
    def p2intersection_distance(self, X, Y, Z, LC_id):
        tmp = self.a.getFeatureByUid('Lane_centerline', LC_id)
        # o = hd_map.OGRPoint(X, Y, Z)
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
        return distance

    # service for get_data_from_location
    def LC_id2Road_info(self, LC_id):
        tmp = self.a.getFeatureByUid('Lane_centerline', LC_id)
        # print(tmp.isValid())
        RC_id = tmp.GetFieldAsInteger64('RC_id')
        return RC_id

    # service for get_data_from_location  
    def LC2intersection(self, LC_id):
        tmp = self.a.getFeatureByUid('Lane_centerline', LC_id)
        # print(tmp.isValid())
        Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
        Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
        return Sec_outer
    
    def light2Sec(self):
        cnt = 0
        tp = defaultdict(list)
        tp_ans = []

        TL_num = self.set_X_info('Traffic_light')
        Sec_num = self.set_X_info('Intersection')
        Lane_num = self.set_X_info('Lane_centerline')
        for i in range(TL_num):
            # lane_info
            # 遍历traffic_light中effectlane不为None的项
            if self.Traffic_light[i][7] != None:
                tp_LC = self.Traffic_light[i][7].split(",")
                # 在LC中 遍历单个feature中的每一个lane_id 对应的feature
                for a in tp_LC:
                    # print(type(a))
                    LC_id = int(a)
                    LC_e_node = -1
                    # 遍历LC查找起始ID
                    for x in self.lanecenterlines:
                        if x[1] == LC_id:
                            LC_e_node = x[3]
                            

                    # 遍历LC查找起始点为真实车道终止点的虚拟车道线UID
                    for y in self.lanecenterlines:
                        # if y[2] == LC_e_node & y[8] == 3:
                        if y[2] == LC_e_node:
                            if y[8] == 3:
                                tp[a].append(y[1])
                                cnt+=1
                            
        l = list(tp.items())
        print(l[0])
                    

                    # tp_f = self.a.getFeatureByUid('Lane_centerline', LC_id)
                    # v = tp_f.GetFieldAsInteger64('Is_virtual')
                    # if v==3:
                    #     # cnt+=1
                    #     print(a)
            # 信号灯控制的虚拟车道是否可以通行
            # # road_info
            # if self.Traffic_light[i][8] != None:
            #     tp_RC = self.Traffic_light[i][8].split(",")
            #     # 遍历traffic_light中effectroad不为None的项
            #     for item in tp_RC:
            #         RC_id = item
            #         # 遍历intersection中in_id包含effectroad的项
            #         for j in range(Sec_num):
            #             if RC_id in self.intersections[j][4]:
            #                 tp_lane = []
            #                 tp_vir_lane = []
            #                 # 遍历LC中的真实车道与虚拟车道并匹配
            #                 for a in self.lanecenterlines:
            #                     if a[4] == RC_id:
            #                         if a[5] == 3:
            #                             # 保存虚拟车道线UID
            #                             tp_vir_lane.append(a[1])
            #                         else:
            #                             tp_lane.append(a[1])
            #                 # print(RC_id)
            #                 # cnt+=1
            
        # print(cnt)   


    # many bug
    # def LC_connection(self, num):
    #     tmp_arr = np.empty((num, num), dtype=object)
    #     cnt1 = 0

    #     for item in self.intersections:
    #         cnt2 = 0

    #         # record sec_Uid
    #         tmp_arr[cnt1][0] = item[1]

    #         pre_in_RCid = item[4]
    #         pre_out_RCid = item[5]
    #         in_id = pre_in_RCid.split(",")
    #         out_id = pre_out_RCid.split(",")

    #         for i in in_id:
    #             tmp1 = self.a.getFeatureByFieldValue('Lane_centerline','RC_id', i)
    #             Is_virtual1 = tmp1.GetFieldAsInteger64('Is_virtual')
    #             if Is_virtual1 == 3:
    #                 for o in out_id:
    #                     tmp2 = self.a.getFeatureByFieldValue('Lane_centerline','RC_id', o)
    #                     Is_virtual2 = tmp2.GetFieldAsInteger64('Is_virtual')
    #                     if Is_virtual2 == 3:
    #                         pair = str(i) + ',' + str(o)
    #                         print(pair)
    #                         tmp_arr[cnt1][cnt2] = pair
    #                         cnt2 = cnt2 + 1
            
    #         cnt1 = cnt1 + 1
        
    #     print(tmp_arr[0])
    #     return 0
    
    # def section2in_rc_id(self, Sec_id):
    #     tmp = self.a.getFeatureByUid('Intersection', Sec_id)
    #     pre_in_id = tmp.GetFieldAsString('In_RC_id')
    #     in_id = pre_in_id.split(",")
    #     return in_id
    
    # def section2out_rc_id(self, Sec_id):
    #     tmp = self.a.getFeatureByUid('Intersection', Sec_id)
    #     pre_in_id = tmp.GetFieldAsString('Out_RC_id')
    #     out_id = pre_in_id.split(",")
    #     return out_id
    

map = HDMapDemo()
# map.set_X_info('Lane_centerline')
# map.set_X_info('Intersection')
# map.set_X_info('Traffic_light')
# map.LC_connection(sec_num)
map.light2Sec()

# i = '111'
# il = ['111', '123344']
# il0 = ['4667','8980']
# if i in il:
#     print("kkk")

# if i in il0:
#     print("qqq")
# else:
#     print("iii")

# map.try_print(1)

# path = 'traffic_light/traffic_light.csv'
# timestamp = 1621960305900090
# map.update_light_status(path=path, timestamp=timestamp)

# print(map.get_data_from_location(664400+40, 3997000-20))
# print(map.get_data_from_location(664400+40, 3997000+40))

# while True:
#     print('input point X, Y')
#     x,y = [float(x) for x in input().strip().replace(',', '').split(' ')]
# x =
# y =
# z = 
# print(map.get_data_from_location(396903.753251160455309, 3418674.60433388105154, 15.888042509815196))


    # def create_sec_feature():
    #     # 创建一个OGRFeatureDefn类型的变量
    #     feature_defn = ogr.FeatureDefn('example')

    #     # 添加一个名为'id'的整数字段
    #     id_field = ogr.FieldDefn('id', ogr.OFTInteger)
    #     feature_defn.AddFieldDefn(id_field)

    #     # 添加一个名为'name'的字符串字段
    #     name_field = ogr.FieldDefn('name', ogr.OFTString)
    #     feature_defn.AddFieldDefn(name_field)

    #     # 添加一个名为'geom'的点几何字段
    #     geom_field = ogr.GeomFieldDefn('geom', ogr.wkbPoint)
    #     feature_defn.AddGeomFieldDefn(geom_field)

    #     # 使用OGRFeatureDefn类型的变量作为参数，创建一个OGRFeature类型的变量
    #     feature = ogr.Feature(feature_defn)

    #     # 设置字段和几何值
    #     feature.SetField('id', 1)
    #     feature.SetField('name', 'Bing')
    #     point = ogr.Geometry(ogr.wkbPoint)
    #     point.AddPoint(0, 0)
    #     feature.SetGeometry(point)