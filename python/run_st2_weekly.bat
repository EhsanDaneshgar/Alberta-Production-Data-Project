@echo off
REM Weekly AER ST2 download - runs aer_st2_download_v1.py and appends output to st2_log.txt
cd /d "C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\ST2"
echo ===== %date% %time% >> st2_log.txt
python aer_st2_download_v1.py >> st2_log.txt 2>&1
