# Helper script to create Qt Designer zip for GitHub releases
# Run this once to prepare Qt Designer for CI builds

Write-Host "=== Qt Designer Packaging Script ===" -ForegroundColor Green

# Check if Qt Designer folder exists
if (-not (Test-Path "Qt Designer\designer.exe")) {
    Write-Host "Error: Qt Designer folder not found!" -ForegroundColor Red
    Write-Host "Make sure 'Qt Designer\designer.exe' exists before running this script." -ForegroundColor Yellow
    exit 1
}

# Get folder size
$folderSize = (Get-ChildItem "Qt Designer" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`nQt Designer folder size: $($folderSize.ToString('F2')) MB" -ForegroundColor Cyan

# Create zip file
Write-Host "`nCreating qt-designer.zip..." -ForegroundColor Cyan
if (Test-Path "qt-designer.zip") {
    Remove-Item "qt-designer.zip" -Force
}

Compress-Archive -Path "Qt Designer" -DestinationPath "qt-designer.zip" -CompressionLevel Optimal

$zipSize = (Get-Item "qt-designer.zip").Length / 1MB
Write-Host "✓ Created qt-designer.zip ($($zipSize.ToString('F2')) MB)" -ForegroundColor Green

Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/walidroid/thonnysc/releases/new"
Write-Host "2. Create a new release with tag: qt-designer"
Write-Host "3. Upload qt-designer.zip to that release"
Write-Host "4. Future CI builds will automatically download Qt Designer"
Write-Host "`nLocal builds will continue to use the Qt Designer folder directly." -ForegroundColor Cyan
