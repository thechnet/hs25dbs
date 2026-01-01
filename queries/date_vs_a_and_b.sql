SELECT
    date,
    $a_metric,
    $b_metric
FROM $a_table
INNER JOIN $b_table USING (date, region)
WHERE
    date BETWEEN $date_begin AND $date_end
    AND region = $region
;
