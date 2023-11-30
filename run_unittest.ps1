#!/bin/sh
echo `# <#`

cd tests
python test_unittest.py
cd ..

exit
#> > $null

cd tests
python test_unittest.py
cd ..
