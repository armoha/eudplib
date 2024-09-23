@echo off

cd ..
pip uninstall -y eudplib
python -m pip install .
cd tools
