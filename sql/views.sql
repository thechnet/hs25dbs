CREATE OR REPLACE VIEW Traffic AS
    SELECT
        day AS date,
        city AS region,
        SUM(occ) / COUNT(occ) AS occ,
        SUM(flow) / COUNT(flow) AS flow
    FROM TrafficMeasurement
    WHERE
        occ < 1 AND -- >=100% occupancy is impossible.
        flow < 3000 -- >=100 cars per minute is unlikely.
    GROUP BY date, region
;

CREATE OR REPLACE VIEW Traffic_augmented AS
    SELECT
        *,
        flow * (1 - occ) AS road_use
    FROM Traffic
;

CREATE OR REPLACE VIEW Zugfahrt_augmented AS
    SELECT
        *,
        CASE
            WHEN haltestellen_name BETWEEN 0 AND 6 THEN 3 -- Basel.
            WHEN haltestellen_name BETWEEN 7 AND 10 THEN 7 -- Luzern.
            ELSE 21 -- Zürich.
        END AS region,
        LEAST(
            3 * 3600, -- Assume a delay of >3h is not weather-related.
            GREATEST(
                0, -- Ignore early arrivals.
                an_prognose - ankunftszeit,
                ab_prognose - abfahrtszeit
            )
        ) AS delay_s
    FROM Zugfahrt
;

CREATE OR REPLACE VIEW Delays AS
    SELECT
        betriebstag AS date,
        region,
        SUM(delay_s) AS total_delay_s
    FROM Zugfahrt_augmented
    GROUP BY date, region
;

CREATE OR REPLACE VIEW Cancellations AS
    SELECT
        betriebstag AS date,
        region,
        COUNT(*) AS cancellations
    FROM Zugfahrt_augmented
    WHERE
        faellt_aus_tf = TRUE
    GROUP BY date, region
;

CREATE OR REPLACE VIEW Snow AS
    SELECT
        date,
        station_location AS region,
        hto000d0 AS snow_cm
    FROM Weather
;

CREATE OR REPLACE VIEW Precipitation AS
    SELECT
        date,
        station_location AS region,
        rre150d0 AS precipitation_mm
    FROM Weather
;

CREATE OR REPLACE VIEW Temperature AS
    SELECT
        date,
        station_location AS region,
        tre200d0 AS temp_avg,
        tre200dn AS temp_min,
        tre200dx AS temp_max
    FROM Weather
;
