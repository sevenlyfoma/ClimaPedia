from flask import Blueprint, request, jsonify
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/src")
import wikidataQuerying
import cacheMaintainance
from logging import DEBUG, INFO
from typing import Dict

import satelliteVisualisations.satelliteMapVisualisationFunctions as satelliteMapVisualisations
import satelliteVisualisations.satelliteTimelineVisualisationFunctions as satelliteTimelineVisualisations
import peopleVisualisation.peopleVisualisationFunctions as peopleVisualisation
import universityVisualisation.universityVisualisationFunctions as universityVisualisations
import voronoiVisualisation.voronoiVisualisationFunctions as voronoiVisualisations

# Chart imports
import charts.peopleInstitutionsPieChart as peopleInstitutionsPieChart
import charts.peopleOverTimeLineChart as peopleOverTimeLineChart

# Don't change this line!
blueprint = Blueprint("group54", __name__)

logger = wikidataQuerying.createLogger(INFO)
cacheMaintainance.init(logger, freq=1)  # refresh cache every hour

DEFAULT_LATITUDE = [-90, 90]
DEFAULT_LONGITUDE = [-180, 180]
DEFAULT_DATES = ["0000-01-01T00:00:00Z", "9999-12-31T24:59:59Z"]


@blueprint.route("/universitiesTimeTree")
def universitiesView() -> str:
    queryParams = request.args
    startDate = (
        queryParams["starttime"] if "starttime" in queryParams else DEFAULT_DATES[0]
    )
    endDate = queryParams["endtime"] if "endtime" in queryParams else DEFAULT_DATES[1]

    if "meta" in queryParams and queryParams["meta"] == "1":
        return jsonify(universityVisualisations.makeMetadata())
    else:
        return jsonify(
            universityVisualisations.institution(startDate=startDate, endDate=endDate)
        )


@blueprint.route("/universitiesTimeTree/<idVal>")
def universitiesPart(idVal: str) -> str:
    queryParams = request.args
    # Splitting the ID value to determine if it's for a university or an
    # individual person
    idParts = idVal.split("_")

    if len(idParts) == 1:
        # Assuming idVal is a university ID, fetch scientists associated
        data = universityVisualisations.scientistName(
            startDate=queryParams["starttime"],
            endDate=queryParams["endtime"],
            uni_id=idVal,
        )
        return jsonify(data)
    else:
        # Assuming idVal is a person ID, generate and return their biography
        personId = int(idParts[1])
        htmlBiography = peopleVisualisation.generateHTMLBiography(personId)
        return jsonify(
            {"widget": {"title": "Biography", "markup": htmlBiography, "size": 1}}
        )


@blueprint.route("/polygonHeatTimePeople")
def voronoiView() -> str:
    # optionally specify start and end dates, latitude and longitude ranges
    # if args are omitted, use default longitudes/latitudes and None dates
    queryParams = request.args
    minLat = (
        float(queryParams["minlatitude"])
        if "minlatitude" in queryParams
        else DEFAULT_LATITUDE[0]
    )
    maxLat = (
        float(queryParams["maxlatitude"])
        if "maxlatitude" in queryParams
        else DEFAULT_LATITUDE[1]
    )
    minLong = (
        float(queryParams["minlongitude"])
        if "minlongitude" in queryParams
        else DEFAULT_LONGITUDE[0]
    )
    maxLong = (
        float(queryParams["maxlongitude"])
        if "maxlongitude" in queryParams
        else DEFAULT_LONGITUDE[1]
    )

    # minLat, maxLat = DEFAULT_LATITUDE
    # minLong, maxLong = DEFAULT_LONGITUDE
    # print("\n")

    startDate = (
        queryParams["starttime"] if "starttime" in queryParams else DEFAULT_DATES[0]
    )
    endDate = queryParams["endtime"] if "endtime" in queryParams else DEFAULT_DATES[1]

    if "meta" in queryParams and queryParams["meta"] == "1":
        dynamicMeta = universityVisualisations.makeMetadata()
        dynamicMeta["reloadForBounds"] = True
        return jsonify(dynamicMeta)
    else:
        return jsonify(
            voronoiVisualisations.getJSONVoronoi(
                minLat, maxLat, minLong, maxLong, startDate, endDate
            )
        )


@blueprint.route("/polygonHeatTimePeople/<groupVal>")
def voronoiPart(groupVal: str) -> str:
    """part protocol for the meteorologist voronoi visualisation.

    Args:
        groupVal (str): used to find people in the area, id of polygon:
            '<startdate>,<enddate>;<latitude>,<longitude>;<radius>'

    Returns:
        Dict: JSON output.
    """
    queryParams = request.args
    htmlWidget = voronoiVisualisations.getVoronoiPart(groupVal)
    return jsonify(
        {"widget": {"title": "People in this area", "markup": htmlWidget, "size": 0}}
    )


@blueprint.route("/peopleTimePoints")
def ungenderedView() -> str:
    return peopleView(False, request.args)


@blueprint.route("/genderedTimePoints")
def genderView() -> str:
    return peopleView(True, request.args)


def peopleView(isGendered, queryParams) -> str:
    """
    Processes the request for the people visualisation and returns the
    json data in protocol format for the Map + Points protocol
        OR
    Processes the meta data request for the people visualisation and
    returns the json data in protocol format for the Map Metadata protocol

    Returns:
        Dict: JSON output.
    """

    startDate = (
        queryParams["starttime"] if "starttime" in queryParams else DEFAULT_DATES[0]
    )
    endDate = queryParams["endtime"] if "endtime" in queryParams else DEFAULT_DATES[1]

    if "meta" in queryParams and queryParams["meta"] == "1":
        return jsonify(universityVisualisations.makeMetadata())
    else:
        return jsonify(
            peopleVisualisation.getJsonForPoints(startDate, endDate, isGendered)
        )


@blueprint.route("/peopleTimePoints/<idVal>")
def ungenderedPart(idVal: str):
    return peoplePart(idVal, False)


@blueprint.route("/genderedTimePoints/<idVal>")
def genderPart(idVal: str):
    return peoplePart(idVal, True)


def peoplePart(idVal: str, isGendered: bool) -> str:
    htmlBiography = peopleVisualisation.generateHTMLBiography(int(idVal))
    return jsonify(
        {"widget": {"title": "biography", "markup": htmlBiography, "size": 1}}
    )


@blueprint.route("/satelliteLaunches")
def satelliteMapData() -> str:
    queryParams = request.args

    startDate = (
        queryParams["starttime"] if "starttime" in queryParams else DEFAULT_DATES[0]
    )
    endDate = queryParams["endtime"] if "endtime" in queryParams else DEFAULT_DATES[1]

    if "meta" in queryParams and queryParams["meta"] == "1":
        return jsonify(satelliteMapVisualisations.makeMapMetadata())
    else:
        return jsonify(
            satelliteMapVisualisations.getMapJsonForPoints(startDate, endDate)
        )


@blueprint.route("/satelliteLaunches/<idVal>")
def satelliteMap(idVal: str) -> str:
    htmlWidget = satelliteMapVisualisations.partHTML(int(idVal))
    return jsonify(
        {"widget": {"title": "Notable Events", "markup": htmlWidget, "size": 0}}
    )


@blueprint.route("/satelliteTimelines")
def satelliteTimelineData() -> str:
    queryParams = request.args

    startDate = (
        queryParams["starttime"] if "starttime" in queryParams else DEFAULT_DATES[0]
    )
    endDate = queryParams["endtime"] if "endtime" in queryParams else DEFAULT_DATES[1]

    if "meta" in queryParams and queryParams["meta"] == "1":
        return jsonify(satelliteMapVisualisations.makeMapMetadata())
    else:
        return jsonify(
            satelliteTimelineVisualisations.getEventsOfSatellites(startDate, endDate)
        )


@blueprint.route("/satelliteTimelines/<idVal>")
def satelliteTimeline(idVal: str) -> str:
    htmlWidget = satelliteTimelineVisualisations.partHTML(int(idVal))
    return jsonify({"widget": {"title": "Event", "markup": htmlWidget, "size": 0}})


@blueprint.route("/peoplePerInstitutionChart")
def peopleInstitutionChart() -> str:
    return jsonify(peopleInstitutionsPieChart.peopleInstitutionsPieChart())


@blueprint.route("/peopleOverTimeLineChart")
def peopleOverTimeChart() -> str:
    return jsonify(peopleOverTimeLineChart.peopleOverTimeLineChart())
