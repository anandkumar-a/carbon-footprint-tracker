@echo off
cd /d "d:\Carbon foot print"
git add .
git commit -m "Update EcoGuide: modular Flask app, integrated modules, cleaned app.py"
git push
echo Push completed!
pause
