USE [AlbertaProductionDB]
GO

/****** Object:  Table [dbo].[Source_Volumetrics_v2]    Script Date: 2026-09-28 10:44:15 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Source_Volumetrics_v2](
	[ProductionMonth] [varchar](50) NULL,
	[OperatorBAID] [varchar](50) NULL,
	[OperatorName] [varchar](150) NULL,
	[ReportingFacilityID] [varchar](50) NULL,
	[ReportingFacilityProvinceState] [varchar](50) NULL,
	[ReportingFacilityType] [varchar](50) NULL,
	[ReportingFacilityIdentifier] [varchar](50) NULL,
	[ReportingFacilityName] [varchar](50) NULL,
	[ReportingFacilitySubType] [varchar](50) NULL,
	[ReportingFacilitySubTypeDesc] [varchar](255) NULL,
	[ReportingFacilityLocation] [varchar](50) NULL,
	[FacilityLegalSubdivision] [varchar](50) NULL,
	[FacilitySection] [varchar](50) NULL,
	[FacilityTownship] [varchar](50) NULL,
	[FacilityRange] [varchar](50) NULL,
	[FacilityMeridian] [varchar](50) NULL,
	[SubmissionDate] [varchar](50) NULL,
	[ActivityID] [varchar](50) NULL,
	[ProductID] [varchar](50) NULL,
	[FromToID] [varchar](50) NULL,
	[FromToIDProvinceState] [varchar](50) NULL,
	[FromToIDType] [varchar](50) NULL,
	[FromToIDIdentifier] [varchar](50) NULL,
	[Volume] [varchar](50) NULL,
	[Energy] [varchar](50) NULL,
	[Hours] [varchar](50) NULL,
	[CCICode] [varchar](50) NULL,
	[ProrationProduct] [varchar](50) NULL,
	[ProrationFactor] [varchar](50) NULL,
	[Heat] [varchar](50) NULL
) ON [PRIMARY]
GO
