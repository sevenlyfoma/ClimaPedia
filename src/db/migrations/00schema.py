"""
Groups 51 & 52 - db/migrations/00schema.py
"""

QUERY = """
DROP TABLE IF EXISTS `version`;
CREATE TABLE `version`(
    `version` INT PRIMARY KEY
);

DROP TABLE IF EXISTS `EventCountries`;
DROP TABLE IF EXISTS `EventTypes`;
DROP TABLE IF EXISTS `Countries`;
DROP TABLE IF EXISTS `Types`;
DROP TABLE IF EXISTS `Events`;
DROP TABLE IF EXISTS `weather_data`;
DROP TABLE IF EXISTS `station`;

CREATE TABLE Events (
    EVENT_ID VARCHAR(20) NOT NULL PRIMARY KEY,
    LATITUDE DECIMAL(30,10),
    LONGITUDE DECIMAL(30,10),
    START_TIME DATE,
    END_TIME DATE,
    ITEM_LABEL VARCHAR(255) NOT NULL
);

CREATE TABLE Types (
    TYPE_ID VARCHAR(20) NOT NULL PRIMARY KEY
);

CREATE TABLE Countries (
    COUNTRY_ID VARCHAR(20) NOT NULL PRIMARY KEY
);

CREATE TABLE EventTypes (
    EVENT_ID VARCHAR(20),
    TYPE_ID VARCHAR(20),
    PRIMARY KEY (EVENT_ID, TYPE_ID),
    FOREIGN KEY (EVENT_ID) REFERENCES Events(EVENT_ID) ON DELETE CASCADE ON UPDATE RESTRICT,
    FOREIGN KEY (TYPE_ID) REFERENCES Types(TYPE_ID) ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE TABLE EventCountries (
    EVENT_ID VARCHAR(20),
    COUNTRY_ID VARCHAR(20),
    PRIMARY KEY (EVENT_ID, COUNTRY_ID),
    FOREIGN KEY (EVENT_ID) REFERENCES Events(EVENT_ID) ON DELETE CASCADE ON UPDATE RESTRICT,
    FOREIGN KEY (COUNTRY_ID) REFERENCES Countries(COUNTRY_ID) ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE TABLE `station`(
    `station_id` CHAR(20) NOT NULL PRIMARY KEY,
    `name` VARCHAR(100),
    `country` CHAR(20),
    `latitude` DECIMAL(30,10),
    `longitude` DECIMAL(30,10),
    `elevation` DECIMAL(30,10),
    `can_id` VARCHAR(9)
);

CREATE TABLE `weather_data`(
    `station` CHAR(20) NOT NULL,
    `measurement_date` DATE NOT NULL,
    PRIMARY KEY (`station`, `measurement_date`),
    -- Monthly Data
    `avg_high_temp` DOUBLE,
    `avg_low_temp` DOUBLE,
    `avg_temp` DOUBLE,
    `ext_high_temp` DOUBLE,
    `ext_low_temp` DOUBLE,
    `precip_total_rain` DOUBLE,
    `precip_total_snow` DOUBLE,
    `precip_total` DOUBLE,
    `snow_grnd_last_day` DOUBLE,
    `wind_dir_max_gust` DOUBLE,
    `wind_speed_max_gust` DOUBLE,
    CONSTRAINT `fk_station`
        FOREIGN KEY (`station`) REFERENCES `station`(`station_id`)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);
"""

def make_migration(conn, cur) -> None:
    cur.execute(QUERY)
