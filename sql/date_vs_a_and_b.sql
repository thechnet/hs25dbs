SELECT
    date,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM Holidays
            WHERE date BETWEEN Holidays.start_date AND Holidays.end_date
        ) THEN 1 ELSE 0
    END as holiday,
    $a_metric,
    $b_metric
FROM $a_table
INNER JOIN $b_table USING (date, region)
WHERE
    date BETWEEN $date_begin AND $date_end
    AND region = $region
;
