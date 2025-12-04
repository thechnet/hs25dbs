CREATE TABLE IF NOT EXISTS TrafficMeasurement (
    day VARCHAR,
    interval INTEGER,
    detid VARCHAR,
    flow INTEGER,
    occ FLOAT,
    error INTEGER,
    city VARCHAR,
    speed INTEGER,
    PRIMARY KEY (day, interval, detid)
);

CREATE TABLE IF NOT EXISTS DetectorLocation (
    detid VARCHAR,
    length FLOAT,
    pos FLOAT,
    fclass VARCHAR,
    road VARCHAR,
    limit_ VARCHAR,
    citycode VARCHAR,
    lanes INTEGER,
    linkid INTEGER,
    long FLOAT,
    lat FLOAT,
    PRIMARY KEY (detid, fclass, citycode)
);

CREATE TABLE IF NOT EXISTS DetectorLink (
    long FLOAT,
    lat FLOAT,
    order_ INTEGER,
    piece VARCHAR,
    linkid VARCHAR,
    group_ VARCHAR,
    citycode VARCHAR,
    PRIMARY KEY (order_, linkid, citycode)
);
