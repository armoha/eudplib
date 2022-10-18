1. Install Python 3.8.10 or later version
2. git clone eudplib
`git clone https://github.com/armoha/eudplib --recursive`
3. Run `pygettext` to update .pot file (PO template file)
```
python C:\YourPythonPath\Tools\i18n\pygettext.py -d C:\eudplibPath\eudplib\localize\base C:\eudplibPath\eudplib
```
4. Run `PoEdit` and open PO template file (.pot)
5. Start localization
![poedit screenshot](img/poedit.jpg)
6. Send a pull request for .po file
