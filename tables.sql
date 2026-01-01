CREATE TABLE IF NOT EXISTS TrafficMeasurement (
    day INTEGER, -- yyyyMMdd (originally "yyyy-MM-dd").
    interval INTEGER, -- in seconds since midnight.
    detid VARCHAR,
    flow FLOAT,
    occ FLOAT,
    error INTEGER,
    city INTEGER, -- e.g. 3 (originally "BAS").
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
    betriebstag INTEGER, -- yyyyMMdd (originally "dd.MM.yyyy").
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
    haltestellen_name INTEGER,
    ankunftszeit INTEGER, -- as timestamp (originally "dd.MM.yyyy HH:mm").
    an_prognose INTEGER, -- as timestamp (originally "dd.MM.yyyy HH:mm:ss").
    an_prognose_status VARCHAR,
    abfahrtszeit INTEGER, -- as timestamp (originally "dd.MM.yyyy HH:mm").
    ab_prognose INTEGER, -- as timestamp (originally "dd.MM.yyyy HH:mm:ss").
    ab_prognose_status VARCHAR,
    durchfahrt_tf BOOLEAN
);

CREATE TABLE IF NOT EXISTS Weather (
    station_location INTEGER, -- e.g. 3 (originally "BAS").
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
    start_date INTEGER, -- yyyyMMdd (originally "yyyy-MM-ddTHH:mm:ss").
    start_time VARCHAR, -- for normalization.
    end_date INTEGER, -- yyyyMMdd (originally "yyyy-MM-ddTHH:mm:ss").
    end_time VARCHAR, -- for normalization.
    summary VARCHAR,
    created_date VARCHAR
);
