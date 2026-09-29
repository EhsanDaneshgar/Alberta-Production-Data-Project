USE [AlbertaProductionDB]
GO

/****** Object:  Table [dbo].[Clean_Volumetrics]    Script Date: 2026-09-28 10:15:28 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Clean_Volumetrics](
	[Production_Month] [date] NOT NULL,
	[Operator_BAID] [varchar](50) NULL,
	[Operator_Name] [varchar](150) NULL,
	[Reporting_Facility_ID] [varchar](50) NULL,
	[Reporting_Facility_Province_State] [varchar](50) NULL,
	[Reporting_Facility_Type] [varchar](50) NULL,
	[Reporting_Facility_Identifier] [varchar](50) NULL,
	[Reporting_Facility_Name] [varchar](50) NULL,
	[Reporting_Facility_Sub_Type] [varchar](50) NULL,
	[Reporting_Facility_Sub_Type_Desc] [varchar](255) NULL,
	[Reporting_Facility_Location] [varchar](50) NULL,
	[Facility_Legal_Subdivision] [varchar](50) NULL,
	[Facility_Section] [varchar](50) NULL,
	[Facility_Township] [varchar](50) NULL,
	[Facility_Range] [varchar](50) NULL,
	[Facility_Meridian] [varchar](50) NULL,
	[Submission_Date] [datetime2](7) NULL,
	[Activity_ID] [varchar](50) NULL,
	[Product_ID] [varchar](50) NULL,
	[From_To_ID] [varchar](50) NULL,
	[From_To_ID_Province_State] [varchar](50) NULL,
	[From_To_ID_Type] [varchar](50) NULL,
	[From_To_ID_Identifier] [varchar](50) NULL,
	[Volume] [decimal](28, 8) NULL,
	[Energy] [decimal](28, 8) NULL,
	[Hours] [decimal](28, 8) NULL,
	[CCI_Code] [varchar](50) NULL,
	[Proration_Product] [varchar](50) NULL,
	[Proration_Factor] [decimal](28, 8) NULL,
	[Heat] [decimal](28, 8) NULL
) ON [PRIMARY]
GO
