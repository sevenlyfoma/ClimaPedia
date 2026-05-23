# Wikidata Weather Project - Innovations and People

## Running the Application
(see top level README.md for full details)

## Directory Structure
 - `src/` contains code for maintaining the cache, querying Wikidata and structuring the data for the visualisations.
    - `src/peopleVisualisation` contains the code for producing the visualisation of the points on the map showing where scientists were born in a given time range.
    - `src/universityVisualisation` contains the code for producing the visualisation of the tree showing which scientists attended which places of higher education in a given time range.
    - `src/voronoiVisualisation` contains the code for producing the voronoi heatmap showing the densities of birth locations for scientists in a given time range - reloading on zoom of the map.
 - `__init__.py` contains the flask blueprints for handling requests to the /group54/ URLs defined in `/manifest.json`
 - `data/` (created upon first run of the backend server) contains the SQLite database cache and any temp files used for persistent timing data such as the last time the cache was refreshed.

## Code Structure (for development purposes)
 - `app.py` is the flask application that imports the blueprint for the endpoint in the `__init__.py` file in each group's directory.
   - `__init__.py` is the endpoint where handlers for visualisations specified in `manifest.json` are implemented.
   - `manifest.json` is the file where the manifest data for each visualisation is written according to the manifest protocol defined on the wiki.
 - `cacheMaintainance.py` contains the code for automatically creating the database and running the thread to maintain it.
   - `queries.py` (used by the cache maintenance thread) contains the SPARQL queries used to acquire the data to be stored in the database.
   - `wikidataQuerying.py` contains the functions used for interrogating Wikidata.

 - `voronoiVisualisationFunctions.py` contains the functions for querying the SQLite database to produce the data for the climatologist density voronoi heatmap.
 - `universityVisualisationFunctions.py` contains the functions for querying the SQLite database to produce the data for the institution-person DAG visualisation.
 - `peopleVisualisationFunctions.py` contains the functions for querying the SQLite database to produce the biographies for each person and the visualisation of climatologists' places of birth.
 - `satelliteMapVisualisationFunctions.py` contains the functions for producing the map-focus visualisation showing the launch information about weather satellites
 - `satelliteTimelineVisualisationFunctions.py` contains the functions for producing the timeline-focus visualisation as an alternative way to visualise the satellite data.

  - `charts` contains the functions for producing chart-focus visualisations such as line graphs and pie charts.

## Running the Unit Tests
(from within backend/)

      python group54/tests/testMain.py

## Database Structure
The following tables represent the structure of the database used to cache the results of the SPARQL query made to the Wikidata endpoint.

### person:
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNo</u> | integer |  | 6194033 |
| name | varchar(255) | not null | "Some guy" |
| DOB | varchar(255) | not null | "1965-04-03T00:00:00Z" |
| latitude | float | not null | 41.504955 |
| longitude | float | not null | 2.105851 |
| location | varchar(255) | not null | "Berlin" |
| occupation | varchar(255) | not null | "meteorologist" |
| DOD | varchar(255) |  | "1969-12-05T00:00:00Z" |
| image_url | varchar(100000) |  | "https://website.com/image.jpg" |
| sex_or_gender | varchar(255) |  | "female" |

### institution:
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNo</u> | integer |  | 216273 |
| name | varchar(255) | not null | "University of things" |
| latitude | float | not null | 41.504955 |
| longitude | float | not null | 2.105851 |

### attending
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNoInstitution</u> | integer | references (institution.QNo) | 216273 |
| <u>QNoPerson</u> | integer | references (person.QNo) | 6194033 |
| isEducation | boolean | not null | TRUE |

### award
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNo</u> | integer |  | 22058866 |
| name | varchar(255) | not null | "Grand Cross of the Order of the Dannebrog" |

### received
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNoAward</u> | integer | references (award.QNo) | 22058866 |
| <u>QNoPerson</u> | integer | references (person.QNo) | 6194033 |

### society
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNo</u> | integer |  | 188771 |
| name | varchar(255) | not null | "French Academy of Sciences" |

### membership
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNoGroup</u> | integer | references (society.QNo) | 188771 |
| <u>QNoPerson</u> | integer | references (person.QNo) | 6194033 |

### satellite
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>QNo</u> | integer |  | 188771 |
| name | varchar(255) | not null | Spacey  |
| latitude | float | not null | 41.504955 |
| longitude | float | not null | 2.105851 |
| image_url | varchar(100000) |  | "https://website.com/image.jpg" |

### satelliteEvent
| Field | Data type | Constraints | Example |
| ----- | --------- | ----------- | ------- |
| <u>EventID</u> | integer | AUTO_INCREMENT | 2 |
| QNoSatellite | integer | references (satellite.QNo) | 78678  |
| name | varchar(255) | not null | Massive Explosion! |
| date | varchar(255) | not null | "1969-12-05T00:00:00Z" |
| isEnd | boolean | not null | true