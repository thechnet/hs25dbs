CREATE INDEX TrafficMeasurementIdx ON TrafficMeasurement (
    day,
    interval,
    occ,
    city
);

CREATE INDEX ZugfahrtIdx ON Zugfahrt (
    betriebstag,
    haltestellen_name,
    ankunftszeit,
    an_prognose
);

CREATE INDEX WeatherIdx ON Weather (
    station_location,
    date,
    hto000d0,
    rre150d0,
    tre200d0,
    tre200dn,
    tre200dx
);

CREATE INDEX BahnhofbelastungIdx ON Bahnhofbelastung (
    Jahr_Annee_Anno_Year,
    Bahnhof_Gare_Stazione_Station,
    Uhrzeit,
    Prozentsatz
);

CREATE INDEX HolidaysIdx ON Holidays (
    start_date,
    end_date
);
