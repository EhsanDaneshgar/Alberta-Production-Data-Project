/*
  AlbertaProductionDB — Stage 5 AER / AGS reference files
  Create separate RAW tables only. No changes to dbo.Source_Well_Infrastructure
  or dbo.Clean_Volumetrics. Run BEFORE the import script.
  Raw values are NVARCHAR to preserve blank cells, leading zeros and source formats.
*/
USE AlbertaProductionDB;
GO

IF OBJECT_ID(N'dbo.AGS_Atlas_Data_Dictionary',N'U') IS NULL
BEGIN
  CREATE TABLE dbo.AGS_Atlas_Data_Dictionary
  (
    [source_file] NVARCHAR(150) NULL,
    [output_file] NVARCHAR(150) NULL,
    [original_code] NVARCHAR(150) NULL,
    [csv_header] NVARCHAR(150) NULL,
    [description] NVARCHAR(500) NULL,
    [unit] NVARCHAR(80) NULL
  );
END;
GO

IF OBJECT_ID(N'dbo.AGS_Atlas_Structure_Tops',N'U') IS NULL
BEGIN
  CREATE TABLE dbo.AGS_Atlas_Structure_Tops
  (
    [well_id] NVARCHAR(150) NULL,
    [lon_nad27] NVARCHAR(80) NULL,
    [lat_nad27] NVARCHAR(80) NULL,
    [kb_elev_m] NVARCHAR(80) NULL,
    [total_depth_m] NVARCHAR(80) NULL,
    [tvd_m] NVARCHAR(80) NULL,
    [bats_battle_kneehills_tuff_structure_m] NVARCHAR(80) NULL,
    [leas_lea_park_pakowki_structure_m] NVARCHAR(80) NULL,
    [milks_milk_river_structure_m] NVARCHAR(80) NULL,
    [bfss_base_of_fish_scales_structure_m] NVARCHAR(80) NULL,
    [cards_cardium_structure_m] NVARCHAR(80) NULL,
    [duns_dunvegan_structure_m] NVARCHAR(80) NULL,
    [viks_viking_structure_m] NVARCHAR(80) NULL,
    [mans_mannville_structure_m] NVARCHAR(80) NULL,
    [smus_sub_mannville_unconformity_m] NVARCHAR(80) NULL,
    [jurs_jurassic_structure_m] NVARCHAR(80) NULL,
    [tris_triassic_structure_m] NVARCHAR(80) NULL,
    [perms_permian_structure_m] NVARCHAR(80) NULL,
    [carbs_carboniferous_structure_m] NVARCHAR(80) NULL,
    [wabs_wabamun_palliser_structure_m] NVARCHAR(80) NULL,
    [wnts_winterburn_structure_m] NVARCHAR(80) NULL,
    [beavs_beaverhill_lake_structure_m] NVARCHAR(80) NULL,
    [elks_elk_point_structure_m] NVARCHAR(80) NULL,
    [ords_ordovician_silurian_structure_m] NVARCHAR(80) NULL,
    [cms_cambrian_lower_ordovician_structure_m] NVARCHAR(80) NULL,
    [prcs_precambrian_structure_m] NVARCHAR(80) NULL
  );
END;
GO

IF OBJECT_ID(N'dbo.AGS_Atlas_Upper_Isopachs',N'U') IS NULL
BEGIN
  CREATE TABLE dbo.AGS_Atlas_Upper_Isopachs
  (
    [well_id] NVARCHAR(150) NULL,
    [lon_nad27] NVARCHAR(80) NULL,
    [lat_nad27] NVARCHAR(80) NULL,
    [kb_elev_m] NVARCHAR(80) NULL,
    [total_depth_m] NVARCHAR(80) NULL,
    [tvd_m] NVARCHAR(80) NULL,
    [kbati1_kb_to_battle_isopach_alberta_m] NVARCHAR(80) NULL,
    [kbati2_kb_to_bearpaw_isopach_saskatchewan_m] NVARCHAR(80) NULL,
    [beari_bearpaw_isopach_alberta_base_surface_m] NVARCHAR(80) NULL,
    [beli_belly_river_isopach_m] NVARCHAR(80) NULL,
    [leai_lea_park_pakowki_isopach_m] NVARCHAR(80) NULL,
    [coli_colorado_isopach_m] NVARCHAR(80) NULL,
    [coli1_milk_river_to_1st_specks_isopach_m] NVARCHAR(80) NULL,
    [coli2_1st_specks_to_2nd_specks_isopach_m] NVARCHAR(80) NULL,
    [coli3_2nd_specks_to_base_of_fish_scales_isopach_m] NVARCHAR(80) NULL,
    [coli4_base_of_fish_scales_to_mannville_isopach_m] NVARCHAR(80) NULL,
    [coli5_1st_specks_to_cardium_isopach_m] NVARCHAR(80) NULL,
    [coli7_base_of_fish_scales_to_viking_isopach_m] NVARCHAR(80) NULL,
    [coli8_cardium_to_2nd_specks_isopach_m] NVARCHAR(80) NULL,
    [cardi_cardium_to_russian_marker_isopach_m] NVARCHAR(80) NULL,
    [duni_dunvegan_isopach_m] NVARCHAR(80) NULL,
    [viki_viking_isopach_m] NVARCHAR(80) NULL,
    [mani_mannville_isopach_m] NVARCHAR(80) NULL,
    [mani1_upper_mannville_isopach_m] NVARCHAR(80) NULL,
    [mani2_lower_mannville_isopach_m] NVARCHAR(80) NULL,
    [mani3_cadomin_cut_bank_isopach_m] NVARCHAR(80) NULL,
    [juri_jurassic_isopach_m] NVARCHAR(80) NULL,
    [juri1_kootenay_nikanassin_isopach_m] NVARCHAR(80) NULL,
    [juri2_fernie_swift_masefield_isopach_m] NVARCHAR(80) NULL,
    [juri3_rierdon_isopach_m] NVARCHAR(80) NULL,
    [juri4_sawtooth_shaunavon_isopach_m] NVARCHAR(80) NULL,
    [juri5_rock_creek_lower_gravelbourg_isopach_m] NVARCHAR(80) NULL,
    [juri6_poker_chip_isopach_m] NVARCHAR(80) NULL,
    [juri7_nordegg_isopach_m] NVARCHAR(80) NULL,
    [juri8_fernie_isopach_m] NVARCHAR(80) NULL
  );
END;
GO

IF OBJECT_ID(N'dbo.AGS_Atlas_Lower_Isopachs',N'U') IS NULL
BEGIN
  CREATE TABLE dbo.AGS_Atlas_Lower_Isopachs
  (
    [well_id] NVARCHAR(150) NULL,
    [lon_nad27] NVARCHAR(80) NULL,
    [lat_nad27] NVARCHAR(80) NULL,
    [kb_elev_m] NVARCHAR(80) NULL,
    [total_depth_m] NVARCHAR(80) NULL,
    [tvd_m] NVARCHAR(80) NULL,
    [tri_triassic_isopach_m] NVARCHAR(80) NULL,
    [tri1_montney_isopach_m] NVARCHAR(80) NULL,
    [tri2_halfway_doig_isopach_m] NVARCHAR(80) NULL,
    [tri3_charlie_lake_isopach_m] NVARCHAR(80) NULL,
    [tri4_pardonet_baldonnel_worsley_isopach_m] NVARCHAR(80) NULL,
    [permi_permian_isopach_m] NVARCHAR(80) NULL,
    [crbi_carboniferous_isopach_m] NVARCHAR(80) NULL,
    [crbi1_stoddart_mattson_kibbey_isopach_m] NVARCHAR(80) NULL,
    [crbi2_rundle_charles_isopach_m] NVARCHAR(80) NULL,
    [crbi3_banff_lodgepole_isopach_m] NVARCHAR(80) NULL,
    [wabfi_wabamun_palliser_isopach_m] NVARCHAR(80) NULL,
    [wti_woodbend_winterburn_isopach_m] NVARCHAR(80) NULL,
    [wti1_winterburn_isopach_m] NVARCHAR(80) NULL,
    [wti2_woodbend_isopach_m] NVARCHAR(80) NULL,
    [wti4_blue_ridge_isopach_m] NVARCHAR(80) NULL,
    [wti5_nisku_isopach_m] NVARCHAR(80) NULL,
    [wti6_upper_ireton_isopach_m] NVARCHAR(80) NULL,
    [wti7_lower_ireton_isopach_m] NVARCHAR(80) NULL,
    [wti8_duvernay_isopach_m] NVARCHAR(80) NULL,
    [wti9_majeau_lake_isopach_m] NVARCHAR(80) NULL,
    [wti10_cooking_lake_isopach_m] NVARCHAR(80) NULL,
    [beavi_beaverhill_lake_isopach_m] NVARCHAR(80) NULL,
    [elki_elk_point_isopach_m] NVARCHAR(80) NULL,
    [ordi_middle_ordovician_lower_devonian_isopach_m] NVARCHAR(80) NULL,
    [ordi1_winnipeg_isopach_m] NVARCHAR(80) NULL,
    [ordi2_red_river_isopach_m] NVARCHAR(80) NULL,
    [ordi3_stony_mountain_isopach_m] NVARCHAR(80) NULL,
    [ordi4_interlake_stonewall_isopach_m] NVARCHAR(80) NULL,
    [cmi_cambrian_lower_ordovician_isopach_m] NVARCHAR(80) NULL,
    [cmi1_middle_cambrian_isopach_m] NVARCHAR(80) NULL,
    [cmi2_upper_cambrian_lower_ordovician_isopach_m] NVARCHAR(80) NULL
  );
END;
GO

IF OBJECT_ID(N'dbo.AER_SDDE_Commingling',N'U') IS NULL
BEGIN
  CREATE TABLE dbo.AER_SDDE_Commingling
  (
    [Unique_Well_Identifier] NVARCHAR(150) NULL,
    [Field] NVARCHAR(150) NULL,
    [Commingling_Process] NVARCHAR(80) NULL,
    [Commingling_Process_Date] NVARCHAR(80) NULL,
    [Licensee] NVARCHAR(500) NULL,
    [Prod_String_UWI] NVARCHAR(150) NULL,
    [Sort_UWI] NVARCHAR(80) NULL
  );
END;
GO

/*
  Safe reference join keys. The AER CPA ID (13 digits) and 13-digit Sort UWI
  follow the same *sort-order convention*; confirm matching empirically.
  The first character before a space in the AGS Atlas well_id is retained
  as source record subtype; it is NOT automatically treated as part of the UWI.
  Some Atlas IDs are non-Alberta/other length; leave those unmatched pending review.
*/
CREATE OR ALTER VIEW dbo.vw_Well_Infrastructure_SortUWI
AS
SELECT
    wi.Well_ID,
    wi.Well_Identifier,
    wi.Licence_Number,
    wi.Field_Code,
    CASE
      WHEN LEN(LTRIM(RTRIM(wi.Well_Identifier))) = 16
       AND SUBSTRING(wi.Well_Identifier, 13, 1) = 'W'
       AND SUBSTRING(wi.Well_Identifier, 14, 1) IN ('4','5','6')
      THEN SUBSTRING(wi.Well_Identifier,8,3)
         + SUBSTRING(wi.Well_Identifier,14,1)
         + SUBSTRING(wi.Well_Identifier,11,2)
         + SUBSTRING(wi.Well_Identifier,6,2)
         + SUBSTRING(wi.Well_Identifier,4,2)
         + SUBSTRING(wi.Well_Identifier,2,2)
         + RIGHT(wi.Well_Identifier,1)
      ELSE NULL
    END AS Sort_UWI
FROM dbo.Source_Well_Infrastructure AS wi;
GO

CREATE OR ALTER VIEW dbo.vw_AGS_Atlas_Well_Keys
AS
WITH AtlasRows AS
(
    SELECT N'Structure_Tops' AS Source_Dataset, well_id AS Atlas_Well_ID
    FROM dbo.AGS_Atlas_Structure_Tops
    UNION ALL
    SELECT N'Upper_Isopachs', well_id
    FROM dbo.AGS_Atlas_Upper_Isopachs
    UNION ALL
    SELECT N'Lower_Isopachs', well_id
    FROM dbo.AGS_Atlas_Lower_Isopachs
), SplitID AS
(
    SELECT Source_Dataset, Atlas_Well_ID,
           LEFT(LTRIM(RTRIM(Atlas_Well_ID)),1) AS Source_Prefix,
           CASE WHEN SUBSTRING(LTRIM(RTRIM(Atlas_Well_ID)),2,1)=N' '
                THEN SUBSTRING(LTRIM(RTRIM(Atlas_Well_ID)),3,150)
                ELSE NULL END AS Payload
    FROM AtlasRows
)
SELECT Source_Dataset, Atlas_Well_ID, Source_Prefix,
       CASE WHEN LEN(Payload)=13 AND Payload NOT LIKE '%[^0-9]%'
            THEN Payload ELSE NULL END AS Sort_UWI,
       CASE WHEN LEN(Payload)=16
                  AND SUBSTRING(Payload,13,1) = 'W'
                  AND SUBSTRING(Payload,14,1) IN ('4','5','6')
            THEN Payload ELSE NULL END AS Identifier_16
FROM SplitID;
GO

/* Audit after import (do not join every row directly to production):
SELECT COUNT_BIG(*) AS AtlasStructureRows FROM dbo.AGS_Atlas_Structure_Tops;
SELECT COUNT_BIG(*) AS AtlasUpperRows     FROM dbo.AGS_Atlas_Upper_Isopachs;
SELECT COUNT_BIG(*) AS AtlasLowerRows     FROM dbo.AGS_Atlas_Lower_Isopachs;
SELECT COUNT_BIG(*) AS DictionaryRows     FROM dbo.AGS_Atlas_Data_Dictionary;
SELECT COUNT_BIG(*) AS ComminglingRows    FROM dbo.AER_SDDE_Commingling;

SELECT TOP(20) Well_ID, Well_Identifier, Sort_UWI, Licence_Number
FROM dbo.vw_Well_Infrastructure_SortUWI
WHERE Licence_Number = '0505674';
*/
