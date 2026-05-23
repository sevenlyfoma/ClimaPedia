from typing import List, Dict, Tuple

class ChartEntry:
    """
        This class represents an entry for a pie chart or bar chart 
        visualisation. It must be converted to a JSON object before being 
        sent to the frontend.
    """
    def __init__(self, label:str, id:str, value:float, defaultColor:str = None)\
            -> None:
        """__init__ for ChartEntry object

        Args:
            label (str): label of chart entry section
            id (str): id of chart entry section to query in part protocol
            value (float): value of the entry
            defaultColor (str, optional): _description_. Defaults to None.
        """
        self.label = label
        self.id = id
        self.value = value
        self.defaultColor = defaultColor

    def toJson(self) -> Dict:
        """produce dict of chart entry

        Returns:
            Dict: python dict object to be used as JSON output
        """
        return {
            "label": self.label,
            "id": self.id,
            "value": self.value,
            "defaultColor": self.defaultColor
        }

    def __getitem__(self, key:str):
        return self.__dict__[key]

    def __setitem__(self, key:str, value) -> None:
        self.__dict__[key] = value
    
    def __str__(self) -> str:
        return str(self.__dict__)

def makeChartEntries(data: List[List]) -> List[ChartEntry]:
    """turn data into list of ChartEntry objects
    
    Args:
        data (List[List[str, str, float]]): data to format for presentation as a
            chart
            
    Returns:
        List[ChartEntry]: chart entries representing the chart.
    """
    chartEntries = []
    for entry in data:
        chartEntries.append(ChartEntry(entry[1], entry[0], entry[2]))
    return chartEntries

def makePieChartMetadata(chartEntries: List[ChartEntry]) \
        -> Dict[str, List[ChartEntry]]:
    """format list of ChartEntry objects as pie chart
    
    Args:
        chartEntries (List[ChartEntry]): chart entries comprising a pie chart
            
    Returns:
        Dict[List[ChartEntry]]: chart to send to frontend
    """

    chartEntriesJSON = []

    for entry in chartEntries:
        x = entry.toJson()
        chartEntriesJSON.append(x)

    return {
        "data": chartEntriesJSON,
    }

def makeBarChartMetaData(chartEntries: List[ChartEntry], 
        isLogarithmic:bool=False, isContinuous:bool=False, 
        is3D:bool=False) -> Dict:
    """format list of ChartEntry objects as bar chart
    
    Args:
        chartEntries (List[ChartEntry]): chart entries comprising a bar chart
        isLogarithmic (bool): whether Y axis scale should be logarithmic
        isContinuous (bool): whether data is continuous (histogram)
        is3D (bool): whether data is 3D
            
    Returns:
        Dict: bar chart to send to frontend
    """
    chartEntriesJSON = []

    for entry in chartEntries:
        x = entry.toJson()
        chartEntriesJSON.append(x)

    return {
        "data": chartEntriesJSON,
        "isLogarithmic": isLogarithmic,
        "isContinous": isContinuous,
        "is3D": is3D
    }

########################### 
#       Line Charts       #
###########################

class Point:
    """
        This class represents a point for a line chart visualisation.
    """
    def __init__(self, x:float, y:float) -> None:
        """__init__ function for creating new Point objects

        Args:
            x (float): x coordinate of point
            y (float): y coordinate of point
        """
        self.x = x
        self.y = y
        # make 'array' to represent the point
        self.array = [x, y]

    def getPoint(self) -> List[float]:
        return self.array

    def __getitem__(self, key: str):
        return self.__dict__[key]

    def __setitem__(self, key: str, value) -> None:
        self.__dict__[key] = value
    
    def __str__(self) -> str:
        return str(self.__dict__)

class Line:
    """
        This class represents a line for a line chart visualisation. 
        Requires an array of points to be passed in.
    """
    def __init__(self, points: List[Point]):
        """__init__ function for creating new Line objects

        Args:
            points (List[Point]): list of points that represent a line.
        """
        self.points = points

    def getLine(self) -> List[Point]:
        return [point.getPoint() for point in self.points]

    def __getitem__(self, key: str) -> List[Point]:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: List[Point]) -> None:
        self.__dict__[key] = value
    
    def __str__(self) -> str:
        return str(self.__dict__)

def makeLineChartMetaData(lines: List[Line], ids:List[str], 
        colours:List[str]=None, styles:Dict=None, clickable:bool=None, 
        isLogarithmic:bool=None, xAxis:Dict=None, yAxis:Dict=None,
        title:Dict=None) -> Dict:
    """function for producing line graphs to send to the front end.

    Args:
        lines (List[Line]): list of points that represent a line.
        ids (List[str]): list of string ids used to query points for the part
            protocol
        styles (Dict): styles to apply to lines
        clickable (bool): whether lines are clickable
        isLogarithmic (bool): whether Y axis is logarithmic
        xAxis (Dict): information about the X axis
        yAxis (Dict): information about the Y axis
        title (str):  title of the graph
        
    Returns:
        Dict: object representing line graph to be sent to the front end.
    """

    linesJSON = [lines[i].getLine() for i in range(len(lines))] 

    metaData = {
        "lines": linesJSON,
        "ids": ids
    }

    if colours:
        metaData["colours"] = colours
    if styles:
        metaData["styles"] = styles
    if clickable:
        metaData["clickable"] = clickable
    if isLogarithmic:
        metaData["isLogarithmic"] = isLogarithmic
    if xAxis:
        metaData["xAxis"] = xAxis
    if yAxis:
        metaData["yAxis"] = yAxis
    if title:
        metaData["title"] = title
    
    return metaData