
USE AlbertaProductionDB;
GO

-- AER ST103 Field / Production Pool / Geological Pool reference table
-- Source: AER FieldPoolList.xlsx
-- Imported source records: 68,515
-- Initial import completed: October 18, 2026

IF OBJECT_ID('dbo.Ref_FieldPool_ST103', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Ref_FieldPool_ST103
    (
        Field_Name            NVARCHAR(100) NULL,
        Production_Pool_Name  NVARCHAR(100) NULL,
        Field_Code            NVARCHAR(4)   NULL,
        Production_Pool_Code  NVARCHAR(7)   NULL,
        Geological_Pool_Code  NVARCHAR(7)   NULL,
        Geological_Pool_Name  NVARCHAR(100) NULL,
        Confidential          NVARCHAR(20)  NULL
    );
END;
GO

-- Data was loaded separately using
-- SQL Server Import and Export Wizard.
-- This script does not import data.
