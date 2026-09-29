SELECT
    (SELECT COUNT_BIG(*)
     FROM dbo.Clean_Volumetrics) AS Clean_Table_Rows,

    (SELECT COUNT_BIG(*)
     FROM dbo.vw_Volumetrics_With_Current_Well_ID) AS View_Rows,

    (SELECT COUNT_BIG(*)
     FROM dbo.vw_Volumetrics_With_Current_Well_ID)
    -
    (SELECT COUNT_BIG(*)
     FROM dbo.Clean_Volumetrics) AS Row_Difference;


SELECT
    Well_ID_Match_Method,
    COUNT_BIG(*) AS Row_Count
FROM dbo.vw_Volumetrics_With_Current_Well_ID
GROUP BY Well_ID_Match_Method
ORDER BY Row_Count DESC;
