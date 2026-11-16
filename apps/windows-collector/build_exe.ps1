# Build standalone TARANG Laptop Hybrid .exe using PyInstaller
python -m pip install pyinstaller
python -m PyInstaller `
  --name "TARANG-Laptop" `
  --onefile `
  --paths "tarang_collector;..\..\services\api" `
  --add-data "..\..\apps\web\dist;apps\web\dist" `
  --add-data "..\..\samples;samples" `
  tarang_collector\__main__.py
Write-Host "Built dist\TARANG-Laptop.exe"
