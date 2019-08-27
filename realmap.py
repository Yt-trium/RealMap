import cv2
from dataclasses import dataclass
import numpy as np
import shapefile

@dataclass
class Cell:
    building: bool = False
    railway: bool = False
    road: bool = False
    waterway: bool = False

# parameters
out_min_x = 0
out_min_y = 0
out_max_x = 96
out_max_y = 60

out_size_x = out_max_x - out_min_x
out_size_y = out_max_y - out_min_y
out_r = out_size_x / out_size_y
out_bbox = (out_min_x, out_min_y, out_max_x, out_max_y)

out_map = [[Cell() for y in range(0, out_size_y+1)] for x in range(0, out_size_x+1)]

print("RealMap")

sf_buildings = shapefile.Reader("example/preprocessed shape/buildings_points_L93")
sf_railways = shapefile.Reader("example/preprocessed shape/railways_points_L93")
sf_roads = shapefile.Reader("example/preprocessed shape/roads_points_L93")
sf_waterways = shapefile.Reader("example/preprocessed shape/waterways_points_L93")


def isValidShape(sf):
    return not (sf.shapeType != shapefile.POINT and
                sf.shapeType != shapefile.POINTM and
                sf.shapeType != shapefile.POINTZ)


if not isValidShape(sf_buildings):
    print("ERROR : buildings are not points or points with m or points with z")
    exit()

if not isValidShape(sf_railways):
    print("ERROR : railways are not points or points with m or points with z")
    exit()

if not isValidShape(sf_roads):
    print("ERROR : roads are not points or points with m or points with z")
    exit()

if not isValidShape(sf_waterways):
    print("ERROR : waterways are not points or points with m or points with z")
    exit()


sf_min_x = min(sf_buildings.bbox[0], sf_railways.bbox[0], sf_roads.bbox[0], sf_waterways.bbox[0])
sf_min_y = min(sf_buildings.bbox[1], sf_railways.bbox[1], sf_roads.bbox[1], sf_waterways.bbox[1])
sf_max_x = max(sf_buildings.bbox[2], sf_railways.bbox[2], sf_roads.bbox[2], sf_waterways.bbox[2])
sf_max_y = max(sf_buildings.bbox[3], sf_railways.bbox[3], sf_roads.bbox[3], sf_waterways.bbox[3])

sf_size_x = sf_max_x - sf_min_x
sf_size_y = sf_max_y - sf_min_y
sf_r = sf_size_x / sf_size_y
sf_bbox = (sf_min_x, sf_min_y, sf_max_x, sf_max_y)

diff_r = out_r / sf_r

if diff_r > 1.25 or diff_r < 0.75:
    print("WARNING : x/y ratio are very different", out_r, sf_r)


def getCellCoord(s_x, s_y):
    x = s_x - sf_min_x
    y = s_y - sf_min_y

    x = x / sf_size_x
    y = y / sf_size_y

    x = x * out_size_x
    y = y * out_size_y

    x = round(x)
    y = round(y)

    return x, y


s_buildings = sf_buildings.shapes()
f_railways = sf_railways.shapes()
f_roads = sf_roads.shapes()
f_waterways = sf_waterways.shapes()


for p in s_buildings:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y].building = True

for p in f_railways:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y].railway = True

for p in f_roads:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y].road = True

for p in f_waterways:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y].waterway = True


# Read tileset and store tiles we want to keep. This section completely depend on the tileset we use.
tileset = cv2.imread("example/tileset/terrain.bmp", cv2.IMREAD_COLOR)
tileset_b = cv2.imread("example/tileset/building.bmp", cv2.IMREAD_COLOR)


def getTile(x, y):
    return tileset[y*16:y*16+16, x*16:x*16+16]


def getTileB(x, y):
    return tileset_b[y*16:y*16+16, x*16:x*16+16]


tile_nature = getTile(0, 0)
tile_road_horizontal = getTile(1, 0)
tile_road_bridge_horizontal = getTile(2, 0)
tile_water_horizontal = getTile(3, 0)
tile_rail_horizontal = getTile(16, 0)
tile_rail_down_right = getTile(17, 0)

tile_road_vertical = getTile(1, 1)
tile_road_bridge_vertical = getTile(2, 1)
tile_water_vertical = getTile(3, 1)
tile_rail_vertical = getTile(16, 1)
tile_rail_down_left = getTile(17, 1)

tile_water = getTile(0, 2)
tile_road_cross = getTile(1, 2)
tile_water_cross = getTile(3, 2)
tile_rail_horizontal_left_end = getTile(16, 2)
tile_rail_up_right = getTile(17, 2)

tile_nature_forest = getTile(0, 3)
tile_rail_horizontal_right_end = getTile(16, 3)
tile_rail_up_left = getTile(17, 3)

tile_road_down_right = getTile(1, 4)
tile_road_down_left = getTile(2, 4)
tile_rail_vertical_up_end = getTile(16, 4)

tile_road_up_down_right = getTile(1, 5)
tile_road_up_down_left = getTile(2, 5)
tile_rail_vertical_down_end = getTile(16, 5)

tile_road_down_left_right = getTile(1, 6)
tile_road_up_left_right = getTile(2, 6)

tile_road_up_right = getTile(1, 7)
tile_road_up_left = getTile(2, 7)


tile_tower_1 = getTileB(0, 0)
tile_tower_2 = getTileB(0, 1)
tile_city_1 = getTileB(1, 0)
tile_city_2 = getTileB(1, 1)
tile_factory = getTileB(2, 1)
tile_alarm_1 = getTileB(5, 0)
tile_alarm_2 = getTileB(5, 1)

out_image = np.zeros((out_size_y*16,out_size_x*16,3), np.uint8)


def applyPartialTile(out_image, x, y, partialTile):
    for i in range(16):
        for j in range(16):
            if not (partialTile[i][j][0] == 0 and partialTile[i][j][1] == 0 and partialTile[i][j][2] == 0):
                out_image[y * 16 + i][x* 16 + j] = partialTile[i][j]
    return out_image


for x in range(0, out_size_x):
    for y in range(out_size_y-1, 0, -1):

        # To the more specific to the less specific.

        # bridges
        if out_map[x][y].waterway and out_map[x][y].road:
            if out_map[x-1][y].road and out_map[x][y-1].road and out_map[x+1][y].road and out_map[x][y+1].road:
                tile = tile_road_cross
            elif out_map[x-1][y].road and out_map[x+1][y].road:
                tile = tile_road_bridge_horizontal
            elif out_map[x][y-1].road and out_map[x][y+1].road:
                tile = tile_road_bridge_vertical
            else:
                tile = tile_road_cross
        # waterways
        elif out_map[x][y].waterway:
            tile = tile_water
        # roads
        elif out_map[x][y].road:
            if out_map[x - 1][y].road and out_map[x][y - 1].road and out_map[x + 1][y].road and out_map[x][y + 1].road:
                tile = tile_road_cross
            elif out_map[x-1][y].road and out_map[x+1][y].road and out_map[x][y+1].road:
                tile = tile_road_up_left_right
            elif out_map[x-1][y].road and out_map[x+1][y].road and out_map[x][y-1].road:
                tile = tile_road_down_left_right
            elif out_map[x+1][y].road and out_map[x][y+1].road and out_map[x][y-1].road:
                tile = tile_road_up_down_right
            elif out_map[x-1][y].road and out_map[x][y+1].road and out_map[x][y-1].road:
                tile = tile_road_up_down_left
            elif out_map[x+1][y].road and out_map[x][y+1].road:
                tile = tile_road_up_right
            elif out_map[x+1][y].road and out_map[x][y-1].road:
                tile = tile_road_down_right
            elif out_map[x-1][y].road and out_map[x][y+1].road:
                tile = tile_road_up_left
            elif out_map[x-1][y].road and out_map[x][y-1].road:
                tile = tile_road_down_left
            elif out_map[x-1][y].road and out_map[x+1][y].road:
                tile = tile_road_horizontal
            elif out_map[x][y-1].road and out_map[x][y+1].road:
                tile = tile_road_vertical
            else:
                tile = tile_road_cross
        # railways
        elif out_map[x][y].railway:
            if out_map[x - 1][y].railway and out_map[x][y - 1].railway and out_map[x + 1][y].railway and out_map[x][y + 1].railway:
                tile = tile_nature_forest
            elif out_map[x-1][y].railway and out_map[x+1][y].railway and out_map[x][y+1].railway:
                tile = tile_nature_forest
            elif out_map[x-1][y].railway and out_map[x+1][y].railway and out_map[x][y-1].railway:
                tile = tile_nature_forest
            elif out_map[x+1][y].railway and out_map[x][y+1].railway and out_map[x][y-1].railway:
                tile = tile_nature_forest
            elif out_map[x-1][y].railway and out_map[x][y+1].railway and out_map[x][y-1].railway:
                tile = tile_nature_forest
            elif out_map[x+1][y].railway and out_map[x][y+1].railway:
                tile = tile_rail_up_right
            elif out_map[x+1][y].railway and out_map[x][y-1].railway:
                tile = tile_rail_down_right
            elif out_map[x-1][y].railway and out_map[x][y+1].railway:
                tile = tile_rail_up_left
            elif out_map[x-1][y].railway and out_map[x][y-1].railway:
                tile = tile_rail_down_left
            elif out_map[x-1][y].railway and out_map[x+1][y].railway:
                tile = tile_rail_horizontal
            elif out_map[x][y-1].railway and out_map[x][y+1].railway:
                tile = tile_rail_vertical
            elif out_map[x+1][y]:
                tile = tile_rail_horizontal_right_end
            elif out_map[x-1][y]:
                tile = tile_rail_horizontal_left_end
            elif out_map[x][y+1]:
                tile = tile_rail_vertical_up_end
            elif out_map[x][y-1]:
                tile = tile_rail_vertical_down_end
            else:
                tile = tile_nature_forest
        # buildings
        elif out_map[x][y].building:
            if x < 2 or x > out_size_x - 2 or y < 2 or y > out_size_y - 2:
                tile = tile_factory
            else:
                if (out_map[x - 1][y].building and out_map[x - 2][y].building
                and out_map[x + 1][y].building and out_map[x + 2][y].building
                and out_map[x][y - 1].building and out_map[x][y - 2].building
                and out_map[x][y + 1].building and out_map[x][y + 2].building):
                    tile = tile_tower_2
                    y_ = out_size_y - y - 2
                    out_image = applyPartialTile(out_image, x, y_, tile_tower_1)
                elif (out_map[x - 1][y].building and out_map[x + 1][y].building
                and out_map[x][y - 1].building and out_map[x][y + 1].building):
                    tile = tile_city_2
                    y_ = out_size_y - y - 2
                    out_image = applyPartialTile(out_image, x, y_, tile_city_1)
                elif (not out_map[x - 1][y].building and not out_map[x + 1][y].building
                  and not out_map[x][y - 1].building and not out_map[x][y + 1].building):
                    tile = tile_alarm_2
                    y_ = out_size_y - y - 2
                    out_image = applyPartialTile(out_image, x, y_, tile_alarm_1)
                else:
                    tile = tile_factory
        else:
            tile = tile_nature

        y_ = out_size_y - y - 1
        out_image[y_ * 16:y_ * 16 + 16, x * 16:x * 16 + 16] = tile


cv2.imshow('Image', out_image)
k = cv2.waitKey(0)

cv2.imwrite("example/result.png", out_image)
