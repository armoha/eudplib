@echo off

cd ..
pip uninstall -y eudplib
del C:\Python34\Lib\site-packages\eudplib\
python setup.py install
cd tools