import shapefile

# parameters
out_min_x = 0
out_min_y = 0
out_max_x = 40
out_max_y = 20

out_size_x = out_max_x - out_min_x
out_size_y = out_max_y - out_min_y
out_r = out_size_x / out_size_y
out_bbox = (out_min_x, out_min_y, out_max_x, out_max_y)

out_map = [[0 for y in range(0, out_size_y+1)] for x in range(0, out_size_x+1)]

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

    print(x,y)

    out_map[x][y] = out_map[x][y] | int("00000001", 2)

for p in f_railways:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y] = out_map[x][y] | int("00000010", 2)

for p in f_roads:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y] = out_map[x][y] | int("00000100", 2)

for p in f_waterways:
    x = p.points[0][0]
    y = p.points[0][1]

    x, y = getCellCoord(x, y)

    out_map[x][y] = out_map[x][y] | int("00001000", 2)

