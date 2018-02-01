# Trump
Auto rename files and content prefix in xcode project 

# Usage
```
python2 proj_rename.py -i ./Quokka -p ./project.pbxproj -s TL -r Quka  -c True
OR
python proj_rename.py --input ./Quokka -project ./project.pbxproj --start TL --replace LD --content True
```

# Introduce

| Key | Introduction |
| :------   | :-------  |
|  -i (--input)  |  Main file path that you want to replace   |
|  -p (--project)  |  Xcode project.pbxproj file path  |
|  -s (--start)  |  The key word that you want to replace  |
|  -r (--replace)  |  The new key word that you want  |
|  -c (--content)  |  Weather change file content  |
|  -h (--help)  |  Get Help  |

