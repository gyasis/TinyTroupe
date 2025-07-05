select * from athena.athenaone.p4phccdxsuggestion
-- where deletedby ='yearendredo'
;

select 
    b.patientid,
    a.*,
    
from 
    athena.athenaone.p4phccdxsuggestion a
left join 
    twice.intertables.patient_chart_crosswalk b
on 
    a.chartid = b.chartid
    
order by patientid
    ;


select 
    b.patientid,
    a.*,
    
from 
    athena.athenaone.p4phccdxsuggestion a
left join 
    twice.intertables.patient_chart_crosswalk b
on 
    a.chartid = b.chartid
    
order by patientid
    ;


select * from twice.intertables.patient_supplement
limit 2
;

select * from twice.public.filtered_hcc_to_add
order by patientid;


select 
     b.testpatientyn,
    b.patient_status_description,
    a.*,
from
    twice.public.filtered_hcc_to_add a
left join 
    twice.intertables.patient_supplement b
on 
    a.patientid = b.patientid
order by a.patientid
limit 2
;

WITH duplicates AS (
    SELECT 
        b.patientid,
        a.hccid,
        COUNT(*) as count
    FROM 
        athena.athenaone.p4phccdxsuggestion a
    LEFT JOIN 
        twice.intertables.patient_chart_crosswalk b
    ON 
        a.chartid = b.chartid
    WHERE 
        YEAR(a.createddatetime) = 2024
    GROUP BY 
        b.patientid, a.hccid
    HAVING 
        COUNT(*) > 1
)
SELECT 
    b.patientid,
    a.*
FROM 
    athena.athenaone.p4phccdxsuggestion a
LEFT JOIN 
    twice.intertables.patient_chart_crosswalk b
ON 
    a.chartid = b.chartid
WHERE 
    YEAR(a.createddatetime) = 2024
    AND (b.patientid, a.hccid) IN (
        SELECT patientid, hccid 
        FROM duplicates
    )
ORDER BY 
    b.patientid, a.hccid, a.createddatetime;






WITH duplicates AS (
    SELECT 
        b.patientid,
        a.hccid,
        COUNT(*) as count
    FROM 
        athena.athenaone.p4phccdxsuggestion a
    LEFT JOIN 
        twice.intertables.patient_chart_crosswalk b
    ON 
        a.chartid = b.chartid
    WHERE 
        YEAR(a.createddatetime) = 2025
        AND a.lastmodifiedby != 'yearendredo'
    GROUP BY 
        b.patientid, a.hccid
    HAVING 
        COUNT(*) > 1
)
SELECT 
    b.patientid,
    a.*
FROM 
    athena.athenaone.p4phccdxsuggestion a
LEFT JOIN 
    twice.intertables.patient_chart_crosswalk b
ON 
    a.chartid = b.chartid
WHERE 
    YEAR(a.createddatetime) = 2025
    AND (b.patientid, a.hccid) IN (
        SELECT patientid, hccid 
        FROM duplicates
    )
    AND a.lastmodifiedby != 'yearendredo'
ORDER BY 
    b.patientid, a.hccid, a.createddatetime;





    WITH duplicates AS (
    SELECT 
        b.patientid,
        a.hccid,
        COUNT(*) as count
    FROM 
        athena.athenaone.p4phccdxsuggestion a
    LEFT JOIN 
        twice.intertables.patient_chart_crosswalk b
    ON 
        a.chartid = b.chartid
    WHERE 
        YEAR(a.createddatetime) = 2025
        AND a.lastmodifiedby != 'yearendredo'
    GROUP BY 
        b.patientid, a.hccid
    HAVING 
        COUNT(*) > 1
)
SELECT 
    b.patientid,
    a.* EXCLUDE (
        CONTEXTID, 
    CONTEXTNAME, 
    CONTEXTPARENTCONTEXTID,
    diagnosiscodesetid, 
    icdcodeallid,
    ruleid
    )
FROM 
    athena.athenaone.p4phccdxsuggestion a
LEFT JOIN 
    twice.intertables.patient_chart_crosswalk b
ON 
    a.chartid = b.chartid
WHERE 
    YEAR(a.createddatetime) = 2025
    AND (b.patientid, a.hccid) IN (
        SELECT patientid, hccid 
        FROM duplicates
    )
    AND a.lastmodifiedby != 'yearendredo'
ORDER BY 
    b.patientid, a.hccid, a.createddatetime;