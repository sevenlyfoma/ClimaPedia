from logging import DEBUG, INFO, Logger, basicConfig, getLogger
from typing import Tuple


def extractQNumberFromURL(url: str) -> int:
    """extracts integer Q number from URL.

    Args:
        url (str): url to extract from.

    Returns:
        int: integer of Q number.
    """
    return int(url.split("/")[-1][1:])


def incrementYearDate(increment: int, initialDate: str) -> str:
    """finds the date increment years after initialDate. Assumes format
    beginning with yyyy.

    Args:
        increment (int): number of years to increment by.
        initialDate (str): base date to increment from.

    Returns:
        str: date string increment years after initialDate.
    """
    newYear = str(int(initialDate[:4]) + increment)
    return newYear + initialDate[4:]


def extractFromVoronoiID(voronoiID: str) -> Tuple[str, str, float, float, float]:
    """extracts components of voronoi ID.

    Args:
        voronoiID (str): string ID.

    Returns:
        Tuple[str,str,float,float,float]: mintime, maxtime, latitude,
            longitude, radius
    """
    parts = voronoiID.split(';')
    times = parts[0].split(',')
    coords = [(float((x:=i.split(','))[0]),float(x[1])) for i in 
        parts[1].split(':')]
    return times[0], times[1], coords

def extractCoords(pointStr:str) -> Tuple[float, float]:
    """extract coordinates from a string of format (coord1 coord2)

    Args:
        pointStr (str): string to extract coordinates from

    Returns:
        Tuple[float, float]: coordinates (latitude, longitude)
    """
    longLat = pointStr.replace(')','').split('(')[-1].split(' ')
    return (float(longLat[0]), float(longLat[1])) # N then E

# logging boilerplate
def createLogger(level: int = INFO) -> Logger:
    """creates a logger object with specified minimum level.

    Args:
        level (int, optional): level to display. Defaults to INFO.

    Returns:
        Logger: logger object to make logs on.
    """
    basicConfig(format="%(asctime)s: %(message)s", level=level)
    return getLogger()


def maybeLog(mes: str, logger: Logger, level: int = INFO) -> None:
    """logs message at specified level with logger if logger is not None.

    Args:
        mes (str): message to log.
        logger (Logger): logger to log with (None if no logger).
        level (int, optional): level to log mes at. Defaults to INFO.
    """
    if logger:
        logger.log(level, mes)
