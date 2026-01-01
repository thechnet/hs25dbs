CREATE TABLE IF NOT EXISTS TrafficMeasurement (
    day VARCHAR,
    interval VARCHAR, -- originally INTEGER
    detid VARCHAR,
    flow FLOAT,
    occ FLOAT,
    error INTEGER,
    city VARCHAR,
    speed FLOAT
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
    citycode VARCHAR
    -- PRIMARY KEY (order_, linkid, citycode)
);

CREATE TABLE IF NOT EXISTS Zugfahrt (
    betriebstag VARCHAR,
    fahrt_bezeichner VARCHAR,
    betreiber_id VARCHAR,
    betreiber_abk VARCHAR,
    betreiber_name VARCHAR,
    produkt_id VARCHAR,
    linien_id INTEGER,
    linien_text VARCHAR,
    umlauf_id INTEGER,
    verkehrsmittel_text VARCHAR,
    zusatzfahrt_tf BOOLEAN,
    faellt_aus_tf BOOLEAN,
    bpuic INTEGER,
    haltestellen_name VARCHAR,
    ankunftszeit VARCHAR,
    an_prognose VARCHAR,
    an_prognose_status VARCHAR,
    abfahrtszeit VARCHAR,
    ab_prognose VARCHAR,
    ab_prognose_status VARCHAR,
    durchfahrt_tf BOOLEAN
);

CREATE TABLE IF NOT EXISTS Weather (
    station_location VARCHAR,
    date INTEGER,
    gre000d0 FLOAT,
    hto000d0 FLOAT,
    nto000d0 FLOAT,
    prestad0 FLOAT,
    rre150d0 FLOAT,
    sre000d0 FLOAT,
    tre200d0 FLOAT,
    tre200dn FLOAT,
    tre200dx FLOAT,
    ure200d0 FLOAT
);

CREATE TABLE IF NOT EXISTS Bahnhofbelastung (
    Jahr_Annee_Anno_Year INTEGER,
    Bahnhof_Gare_Stazione_Station VARCHAR,
    bpuic INTEGER,
    Uhrzeit TIME, -- originally FLOAT
    Prozentsatz FLOAT
);

CREATE TABLE IF NOT EXISTS Holidays (
    id SERIAL PRIMARY KEY, -- to simplify REST API
    start_date VARCHAR,
    start_time VARCHAR, -- for normalization
    end_date VARCHAR,
    end_time VARCHAR, -- for normalization
    summary VARCHAR,
    created_date VARCHAR
);
