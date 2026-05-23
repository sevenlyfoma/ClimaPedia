from numpy.typing import NDArray

from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import Voronoi

MAX_BOUNDS = [[-1000, 0], [1000, 0], [0, 1000], [0, -1000]]


ONTARIO_BOUNDS = Polygon(
    [
        [45.205168, -74.344077],  # Eastern most
        [46.423, -78.849],  # Quebec border
        [47.424824117493074, -79.5956452261537],  # Quebec south
        [51.4634, -79.5355],  #
        [55.104, -82.408],  # Quebec northern lake
        [56.856944, -88.884722],  # Northern most
        [52.839, -95.125],  # Western spike
        [51.0, -95.153056],  # Western most
        [49.379, -95.120],  # South western
        [48.117, -91.505],
        [48.3275, -88.3589],  # Lake Superior
        [46.905, -84.957],  # Great lakes
        [45.352, -82.463],  # Lake Huron
        [43.5908, -82.1049],  # Lake Huron South
        [42.1995, -83.1143],  # Detroit
        [41.681389, -82.682222],  # Southern most
        [42.8412, -78.9478],  # Buffalo
        [43.4547, -79.2101],  # Lake Ontario
        [43.6415, -76.8082],  # Lake Ontario East
    ]
)

CANADA_BOUNDS = Polygon(
    # Bounds taken via Open Street Maps and Google Maps
    [
        [47.523611, -52.619444],  # Easternmost
        [54.712, -56.854],
        [58.40, -62.23],
        [66.79, -60.82],  # Baffin Island south
        [72.71, -73.21],
        [78.12, -74.71],
        [82.32, -60.21],
        [83.111389, -69.958333],  # Northernmost
        [82.279, -87.847],
        [79.656, -104.810],  # Elif Ringer Island
        [77.157, -120.586],  # Prince Patrick Island
        [71.539, -126.914],  # Banks Island
        [69.61381356540167, -140.48046665556356],  # Alaska north
        [60.306389, -141.001944],  # Westernmost
        [55.285, -129.919],
        [54.304, -133.347],  # Graham Island
        [51.062, -129.847],
        [48.29455931158522, -123.2537672682892],  # Victoria, BC
        [49.03727632303212, -123.30587371863112],  # Vancouver
        [49.01172530005075, -95.16670043949556],  # America spike low
        [49.402207840981156, -95.11995262446452],  # America spike
        [49.379, -95.120],  # South western
        [48.117, -91.505],
        [48.3275, -88.3589],  # Lake Superior
        [46.905, -84.957],  # Great lakes
        [45.352, -82.463],  # Lake Huron
        [43.5908, -82.1049],  # Lake Huron South
        [42.1995, -83.1143],  # Detroit
        [41.681389, -82.682222],  # Southernmost
        [42.8412, -78.9478],  # Buffalo
        [43.4547, -79.2101],  # Lake Ontario
        [43.6415, -76.8082],  # Lake Ontario East
        [45.02069621946876, -74.8106235308455],  # Cornwall, ON
        [45.4236223997116, -70.8043462288686],  # Woburn, QC
        [47.46127563450336, -69.22416969784096],  # Pohenegamook, QC
        [47.06596548222408, -67.78310061900339],  # Grand falls
        [43.423090104919325, -65.615119544898],  # NS
    ]
)


def create_voronoi(
    points: NDArray, values: NDArray, bounding: Polygon
) -> tuple[list, list]:
    """Create a Voronoi map for a set of points and values in Ontario.

    Parameters:
        points: (n_points, 2) A set of points.
        values: (n_points,) A matching set of associated values.
        bounding: The bounding polygon.

    Returns:
        polys: A set of polygons.
        out_vals: An associated set of values.
    """
    voronoi = Voronoi(points.tolist() + MAX_BOUNDS)

    polys = []
    out_vals = []

    for i, r_i in enumerate(voronoi.point_region):
        verts = [
            tuple(voronoi.vertices[x]) if x != -1 else None
            for x in voronoi.regions[r_i]
        ]

        if None not in verts:
            intersection = Polygon(verts).intersection(bounding)
            if isinstance(intersection, Polygon):
                poly = intersection
            elif isinstance(intersection, MultiPolygon):
                # We sometimes get multiple back, pick the biggest.
                poly = max(list(intersection.geoms), key=lambda x: x.area)
            else:
                continue

            polys.append(list(poly.exterior.coords))
            out_vals.append(values[i])

    return (polys, out_vals)
