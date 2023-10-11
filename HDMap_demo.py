from map import Map
import hd_map
from osgeo import ogr
# import gdal
# import ogr
import numpy as np
from tqdm import tqdm
from collections import defaultdict

# 继承map.py中的class Map
class HDMap(Map):
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
        self.L2Light_flag = {}


        for i in range(self.set_X_info('Traffic_light')):
            if self.Traffic_light[i][7] != None:
                tp_LC = self.Traffic_light[i][7].split(",")
                for a in tp_LC:
                    LC_id = int(a)
                    self.L2Light_flag[LC_id] = 1
        
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
    
    # wrong_problem && service for get_data_from_location
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
    

    def lane_is_in_intersection(self, L_id):
        tmp = self.a.getFeatureByUid('Lane_centerline', L_id)
        # print(tmp.isValid())
        Sec_inter = tmp.GetFieldAsInteger64('Sec_inter')
        Sec_outer = tmp.GetFieldAsInteger64('Sec_outer')
        if Sec_inter == 0 & Sec_outer == 0:
            return False
        else:
            return True
        

    def lane_has_traffic_control_measure(self, L_id):
        if L_id in self.lanecenterlineconnectors.keys():
            return self.lanecenterlineconnectors[L_id]["has_traffic_light"]
        return False
    
    # 找到traffic light中 真实车道-虚拟车道-真实车道的数组并返回
    def Lane_r2v2r_Light(self):
        # cnt = 0
        tp = []
        # tp_ans = []

        TL_num = self.set_X_info('Traffic_light')
        # Sec_num = self.set_X_info('Intersection')
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
                        if y[2] == LC_e_node:
                            if y[8] == 3:
                                tp_ = []
                                tp_.append(LC_id)
                                tp_.append(y[1])
                                tp_.append(self.Traffic_light[i][1])
                                tp.append(tp_)
                                # cnt+=1
        # l中保存r2v2r的第一个过程——>r2v
        # l = list(tp.items())
        # print(cnt)
        # print(tp[0])
        # [14027556, 14027595, 2772]

        tp_v = []

        for b in tp:
            r_lane = int(b[0])
            # for c in b[1]:
            LC_id = b[1]
            LC_e_node = -1
            for x in self.lanecenterlines:
                if x[1] == LC_id:
                    LC_e_node =x[3]

            for y in self.lanecenterlines:
                if y[2] == LC_e_node:
                    if y[8] != 3:
                        tp_item = []
                        tp_item.append(r_lane)
                        tp_item.append(LC_id)
                        tp_item.append(y[1])
                        tp_item.append(b[2])
                        tp_v.append(tp_item)

        # print(tp_v[0])
        # [14027556, 14027595, 14027475, 2772]

        return tp_v
    
        # 找到traffic light中 真实车道_虚拟车道-真实车道的数组并返回
    
    def Light2Sec(self):
        cnt = 0

        arr = self.Lane_r2v2r_Light()
        TL_num = self.set_X_info('Traffic_light')
        print(111)
        Sec_num = self.set_X_info('Intersection')
        print(111)
        Lane_num = self.set_X_info('Lane_centerline')
        print(111)

        ans = []

        for item in tqdm(arr):
            r1 = -1
            r2 = -1
            for i in self.lanecenterlines:
                # 起始真实车道 与 终止真实车道分别位于的RC_id
                if item[0] == i[1]:
                    r1 = i[4]

                if item[2] == i[1]:
                    r2 = i[4]

                for j in self.intersections:
                    if str(r1) in j[4]:
                        if str(r2) in j[5]:
                            tp = []
                            tp.append(item[3])
                            tp.append(j[1])
                            ans.append(tp)
                            cnt+=1

        print(cnt)
        print(ans[0])

    def update_light_status_from_csv():
        ...

    def Light2V_Lane(self, tl_id):
        ans = []

        arr = self.Lane_r2v2r_Light()
        for i in arr:
            if (i[3]==tl_id):
                ans.append(i[1])

        return ans
    
    def lane_has_traffic_control_measure(self, L_id):
        flag = self.L2Light_flag.get(L_id)
        if flag == 1:
            return True
        else:
            return False
    
def test_map():
    map = HDMap()
    print('init done')
    # map.set_X_info('Lane_centerline')
    # map.set_X_info('Intersection')
    # map.set_X_info('Traffic_light')
    # map.LC_connection(sec_num)
    # a = map.Lane_r2v2r_Light()
    # a = map.Light2V_Lane(2772)
    # print(a)
    # a = map.lane_is_in_intersection(14027477)
    a = map.lane_has_traffic_control_measure(1)
    if a==0:
        print("uuu")
    else:
        print("qqqq")
    # print(a[0])

test_map()