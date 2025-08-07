@echo off
REM Activate conda environment 'seleenv' and run mf4_importer_gui.py
call conda activate seleenv
python gui\mf4_importer_gui.py
pause