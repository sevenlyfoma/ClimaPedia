import os
import sys
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from cacheMaintainance import queryDatabase, DATABASE_PATH
from scipy.spatial import Voronoi
import sqlite3

import auxiliaryFunctions
import cacheMaintainance
import shapely.geometry as shapely
from scipy.spatial import Voronoi


class Node:
    """class representing the clusters in the Voronoi diagram.
    """
    def __init__(self, latitude:float, longitude:float):
        """init method

        Args:
            y (float): y coord of cluster centre (latitude).
            x (float): x coord of cluster centre (longitude).
        """
        self.x = longitude
        self.y = latitude
        self.count = 0
        self.polygon: shapely.Polygon = None
        self.density: float = None

    def __str__(self) -> str:
        """overridden __str__() implementation. Used for debugging.

        Returns:
            str: string representation of the object.
        """
        return f'{{Node ({self.x},{self.y}) - {str(self.count)} \
            - {self.polygon}}}'

    def __repr__(self) -> str:
        """overridden __repr__() implementation. Used for debugging.

        Returns:
            str: string representation of the object for printing as part of
                another object.
        """
        return self.__str__()


def retrievePoints(startDate:str, endDate:str,
        latRange:Tuple[float,float]=None,
        longRange:Tuple[float, float]=None) \
        -> List[Tuple[float, float]]:
    """Runs SQL query to retrieve coordinates of person.
    
    Args:
        startDate (str, optional): start date for filtering.
        endDate (str, optional): end date for filtering.
        latRange (Tuple[float, float]): maximum and minimum latitude being
            viewed.
        longRange (Tuple[float, float]): maximum and minimum longitude being
            viewed.

    Returns:
        List[Tuple[float, float]]: list of (latitude, longitude) pairs.
    """
    
    baseQuery = """SELECT latitude, longitude FROM person 
        WHERE (longitude BETWEEN ? AND ?) 
        AND (latitude BETWEEN ? AND ?) 
        AND (date(dob) <= ? AND (date(IFNULL(dod, DATE(dob, '+72 years'))) >= ?));"""

    data = queryDatabase(baseQuery,(latRange[0], latRange[1], longRange[0],
                           longRange[1], endDate, startDate))
    return data


def updateDensities(
    shapes: List[Tuple[Node, List[Tuple[float, float]]]], 
    bounds: shapely.Polygon
):
    """updates the polygon and densities of the list of nodes.

    Args:
        shapes (List[Tuple[Node,List[Tuple[float,float]]]]): list of shapes
            and their polygons.
        bounds (shapely.Polygon): polygon of latitude and longitude bounds.
    """
    for node, polygon in shapes:
        node.polygon = shapely.Polygon(polygon).intersection(bounds)
        node.density = node.count / node.polygon.area


def calculateVoronoiRegions(bounds: shapely.Polygon, nodes: List[Node]):
    """produces list of polygons from Voronoi object.

    Args:
        bounds (shapely.Polygon): bounding box of latitudes and longitudes.
        nodes (List[Node]): polygon generating points
    """
    points = [[nodeObj.x, nodeObj.y] for nodeObj in nodes]
    points = points + [[-1000, 0], [1000, 0], [0, 1000], [0, -1000]]
    vor = Voronoi(points)

    polygons = []
    for index in range(len(vor.regions) - 1):
        indexNew = index + 1
        verts = list(
            map(
                lambda i: tuple(vor.vertices[i]) if i != -1 else None,
                vor.regions[indexNew],
            )
        )
        polygons.append(verts)

    combined = [
        (nodes[i], polygons[vor.point_region[i] - 1]) 
            for i in range(len(nodes))
    ]
    completeShapes = list(filter(lambda x: not None in x[1], combined))
    updateDensities(completeShapes, bounds)
    return completeShapes


def getClusters(
    latRange: Tuple[float, float],
    longRange: Tuple[float, float],
    startDate: str,
    endDate: str,
    density: float = 0.1,
) -> List[Node]:
    """Clusters points within a radius determined by the cluster density,
    length and width of the view. This is technically O(n) time complexity as
    there is a finite amount of possible clusters on a given map where the
    centre of an arbitrary cluster is not within any other cluster's area.

    Args:
        latRange (Tuple[float, float]): maximum and minimum latitude being
            viewed.
        longRange (Tuple[float, float]): maximum and minimum longitude being
            viewed.
        startDate (str, optional): start date for filtering. Defaults to None.
        endDate (str, optional): end date for filtering. Defaults to None.
        density (float, optional): magic density for clustering. Defaults to
            0.1.

    Returns:
        List: list of cluster points and weightings
    """
    radius = (latRange[1] - latRange[0]) * density
    points = retrievePoints(startDate, endDate, latRange, longRange)
    if len(points) == 0:
        return [[], 0]

    centres = []
    f = lambda first, second: ((first.y - second[0]) ** 2) + (
        (first.x - second[1]) ** 2
    )

    for point in points:
        close = [cent for cent in centres if f(cent, point) <= (radius**2)]
        if len(close) == 0:
            centres.append(Node(point[0], point[1]))

    for point in points:
        minPoint = min(centres, key=lambda x: f(x, point))
        minPoint.count += 1
    return centres, radius

def getInPoly(ID:str) -> List:
    startTime, endTime, points = \
        auxiliaryFunctions.extractFromVoronoiID(ID)
        
    conn = sqlite3.connect(DATABASE_PATH)
    # hacky, 
    poly = shapely.Polygon(points)
    conn.create_function("polyContains", 2, 
        lambda x,y:poly.contains(shapely.Point(x,y)))
    cur = conn.cursor()
    ret = cur.execute(f"""SELECT name
        FROM person
        WHERE (date(dob) <= ? 
        AND (date(IFNULL(dod, DATE(dob, '+72 years'))) >= ?))
        AND polyContains(longitude, latitude)""",
        [endTime, startTime])
    
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def getVoronoiPart(ID:str) -> Dict:
    namesInPoly = list(map(lambda x:x[0],getInPoly(ID)))
    namesListHTML = "<html><body><ul><li>" + "</li><li>".join(namesInPoly) \
        + "</li></ul></body></html>"
    return f'<html><body>{namesListHTML}</body></html>'


def getJSONVoronoi(
    minlatitude: float,
    maxlatitude: float,
    minlongitude: float,
    maxlongitude: float,
    startdate: str,
    enddate: str,
) -> Dict:
    """
    Formats data to the Map + Voronoi-Heat protocol found at
    https://gitlab.cs.st-andrews.ac.uk/cs3099sg5/project-code/-/wikis/Protocol
    (Accessed 04/11/2023)
    """
    clusters, radius = getClusters(
        (minlatitude, maxlatitude), 
        (minlongitude, maxlongitude), 
        startdate, 
        enddate
    )

    vertices, ids, areas = [], [], []
    bounds = shapely.Polygon(
        [
            (minlatitude, minlongitude),
            (maxlatitude, minlongitude),
            (maxlatitude, maxlongitude),
            (minlatitude, maxlongitude),
        ]
    )
    shapes = calculateVoronoiRegions(bounds, clusters)

    for node in shapes:
        vertices.append(list(node[0].polygon.exterior.coords))
        verts = ":".join([f"{i[0]},{i[1]}" \
            for i in list(node[0].polygon.exterior.coords)])
        ids.append(f'{startdate},{enddate};{verts}')
        areas.append(node[0].density)

    if areas != []:
        jsonData = {
            "polygons": vertices,
            "ids": ids,
            "values": areas,
            "valuesLegend": {
                "valueRange": [min(areas), max(areas)],
                "colourRange": ["yellow", "blue"]
            },
            "clickable": True
        }
    else:
        jsonData = {
            "polygons": [],
            "ids": [],
            "values": [],
            "clickable": True
        }
    return jsonData