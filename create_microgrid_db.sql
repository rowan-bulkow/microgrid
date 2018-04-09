-- run from prompt:
-- mysql -u username -p < file.sql

CREATE DATABASE IF NOT EXISTS microgriddb;
use microgriddb;

create table weather (
    date DATE,
    location VARCHAR(100),
    tempLow FLOAT,
    tempAvg FLOAT,
    tempHigh FLOAT,
    dewLow FLOAT,
    dewAvg FLOAT,
    dewHigh FLOAT,
    humidLow FLOAT,
    humidAvg FLOAT,
    humidHigh FLOAT,
    seaLow FLOAT,
    seaAvg FLOAT,
    seaHigh FLOAT,
    visLow FLOAT,
    visAvg FLOAT,
    visHigh FLOAT,
    windLow FLOAT,
    windAvg FLOAT,
    windHigh FLOAT,
    precipitation FLOAT,
    events VARCHAR(100),
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
    time FLOAT NOT NULL,
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
