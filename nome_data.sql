-- Create table of nome city data from existing data in other tables
use microgriddb;
DROP TABLE IF EXISTS nome_city_feeder;

create table nome_city_feeder (
    date DATETIME,
    temp FLOAT,
    dewpoint FLOAT,
    humidity FLOAT,
    wind VARCHAR(50),
    speed FLOAT,
    gust FLOAT,
    pressure FLOAT,
    precip_rate FLOAT,
    precip_accum FLOAT
);

insert into nome_city_feeder (date, temp, dewpoint, humidity, wind, speed, gust, pressure, precip_rate, precip_accum)
select date, temp, dewpoint, humidity, wind, speed, gust, pressure, precip_rate, precip_accum
from weather
where location = 'KAKNOME1';

UPDATE nome_city_feeder,power_time_values
SET nome_city_feeder.amps = AVG(power_time_values.value)
WHERE TIMESTAMPDIFF(MINUTE,nome_city_feeder.date,FROM_UNIXTIME(power_time_values.time)) < 10
GROUP BY nome_city_feeder.date;

UPDATE nome_city_feeder
JOIN (
    SELECT nome_city_feeder.date as date, AVG(power_time_values.value) as value
    FROM nome_city_feeder
    JOIN power_time_values on TIMESTAMPDIFF(MINUTE,
                                            CONVERT_TZ(nome_city_feeder.date,'-08:00','+00:00'),
                                            FROM_UNIXTIME(power_time_values.time)) < 10
    GROUP BY nome_city_feeder.date
) as power on power.date = nome_city_feeder.date
SET nome_city_feeder.amps = power.value;

update nome_city_feeder, power_time_values
set nome_city_feeder.amps = power_time_values.value
where CONVERT_TZ(nome_city_feeder.date,'-08:00','+00:00') = FROM_UNIXTIME(power_time_values.time);
