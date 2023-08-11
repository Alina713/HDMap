from map import HDMap
import hd_map
from osgeo import ogr

class HDMapDemo(HDMap):
    # 可修改为anting
    map_name = 'lingang'
    a = hd_map.HDMap()

    def __init__(self):
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Traffic_light.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Lane_boundary.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Lane_centerline.shp')
        self.a.readFromSqlLite('../HDMap/' + self.map_name +'/shp_utm/Road_centerline.shp')

        self.lanecenterlines = {}
        self.lanecenterlineconnectors = {}
        self.laneboundaries = {}
        self.laneboundaryconnectors = {}
        self.intersections = {}
        self.R2LC = {}
        self.RC2LCC = {}
        self.LCCstatus = {}
        
        # self._get_intersections()
        # self._get_real_lanes()
        # self._get_virtual_lanes()
        # pass

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
    

map = HDMapDemo()
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
print(map.get_data_from_location(396903.753251160455309, 3418674.60433388105154, 15.888042509815196))