USE [AlbertaProductionDB]
GO

/****** Object:  View [dbo].[vw_Volumetrics_With_Current_Well_ID]    Script Date: 2026-09-28 10:26:14 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [dbo].[vw_Volumetrics_With_Current_Well_ID]
AS

WITH Current_Wells AS
(
    SELECT DISTINCT Well_ID
    FROM dbo.Source_Well_Infrastructure
),
Unique_Previous_Wells AS
(
    SELECT
        Previous_Well_ID,
        MAX(Well_ID) AS Current_Well_ID
    FROM dbo.Source_Well_Infrastructure
    WHERE Previous_Well_ID IS NOT NULL
    GROUP BY Previous_Well_ID
    HAVING COUNT(DISTINCT Well_ID) = 1
)

SELECT
    v.*,

    CASE
        WHEN v.From_To_ID_Type = 'WI'
            THEN COALESCE(c.Well_ID, p.Current_Well_ID)
        ELSE NULL
    END AS Current_Well_ID,

    CASE
        WHEN v.From_To_ID_Type <> 'WI'
            THEN 'Not a Well'
        WHEN c.Well_ID IS NOT NULL
            THEN 'Current Well ID'
        WHEN p.Current_Well_ID IS NOT NULL
            THEN 'Unique Previous Well ID'
        ELSE 'Unmatched'
    END AS Well_ID_Match_Method

FROM dbo.Clean_Volumetrics AS v

LEFT JOIN Current_Wells AS c
    ON v.From_To_ID = c.Well_ID

LEFT JOIN Unique_Previous_Wells AS p
    ON v.From_To_ID_Identifier = p.Previous_Well_ID;
GO
