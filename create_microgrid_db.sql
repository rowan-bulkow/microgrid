-- run from prompt:
-- mysql -u username -p < file.sql

CREATE DATABASE IF NOT EXISTS microgriddb;
use microgriddb;

-- Table to store weather data, specifically that from a 'personal weather station' page from wundergound
-- # Time	Temperature	Dew Point	Humidity	Wind	Speed	Gust	Pressure	Precip. Rate.	Precip. Accum.
-- # 12:00 AM	5.4 F	0.6 F	80 %	SE	2 mph	3 mph	30.37 in	0 in	0 in
create table weather (
    date DATETIME,
    location VARCHAR(100),
    temp FLOAT,
    dewpoint FLOAT,
    humidity FLOAT,
    wind VARCHAR(50),
    speed FLOAT,
    gust FLOAT,
    pressure FLOAT,
    precip_rate FLOAT,
    precip_accum FLOAT,
    CONSTRAINT weatherid PRIMARY KEY (date, location)
);

create table power_sources (
    id INT NOT NULL AUTO_INCREMENT,
    startDate DATE NOT NULL,
    sourceName VARCHAR(250) NOT NULL,
    numTime INT NOT NULL,
    timeUnits VARCHAR(10),
    startTime FLOAT NOT NULL,
    numDays INT NOT NULL,
    description VARCHAR(100),
    samplingRate FLOAT,
    powerUnits VARCHAR(10) NOT NULL,
    rangeMax FLOAT,
    rangeMin FLOAT,
    monthlyMin FLOAT,
    monthlyMax FLOAT,
    monthlyMean FLOAT,
    monthlyStdDev FLOAT,
    powerType VARCHAR(100),
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    placeName VARCHAR(100),
    measurementType VARCHAR(250),
    PRIMARY KEY (id),
    CONSTRAINT UniqueSource UNIQUE (startDate, sourceName)
);

create table power_time_values (
    sourceId INT NOT NULL,
    time DOUBLE PRECISION NOT NULL,
    value FLOAT NOT NULL,
    PRIMARY KEY (sourceId, time),
    FOREIGN KEY (sourceId) REFERENCES power_sources(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

create table power_day_values (
    sourceId INT NOT NULL,
    day INT NOT NULL,
    dailyMin FLOAT NOT NULL,
    dailyMax FLOAT NOT NULL,
    dailyMean FLOAT NOT NULL,
    dailyStdDev FLOAT NOT NULL,
    PRIMARY KEY (sourceId, day),
    FOREIGN KEY (sourceId) REFERENCES power_sources(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- This is an old weather table, meant to store per-day data from the custom history page
-- create table weather (
--     date DATE,
--     location VARCHAR(100),
--     tempLow FLOAT,
--     tempAvg FLOAT,
--     tempHigh FLOAT,
--     dewLow FLOAT,
--     dewAvg FLOAT,
--     dewHigh FLOAT,
--     humidLow FLOAT,
--     humidAvg FLOAT,
--     humidHigh FLOAT,
--     seaLow FLOAT,
--     seaAvg FLOAT,
--     seaHigh FLOAT,
--     visLow FLOAT,
--     visAvg FLOAT,
--     visHigh FLOAT,
--     windLow FLOAT,
--     windAvg FLOAT,
--     windHigh FLOAT,
--     precipitation FLOAT,
--     events VARCHAR(100),
--     CONSTRAINT weatherid PRIMARY KEY (date, location)
-- );

-- another old weather table, for data from daily history page
-- create table weather (
--     date DATETIME,
--     location VARCHAR(100),
--     temp FLOAT,
--     windchill FLOAT,
--     dewpoint FLOAT,
--     humidity FLOAT,
--     pressure FLOAT,
--     visibility FLOAT,
--     winddir VARCHAR(50),
--     windspeed FLOAT,
--     gustspeed FLOAT,
--     precipitation FLOAT,
--     events VARCHAR(100),
--     conditions VARCHAR(250),
--     CONSTRAINT weatherid PRIMARY KEY (date, location)
-- );
