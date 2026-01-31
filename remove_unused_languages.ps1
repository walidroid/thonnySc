# Remove all language folders except English and French
# Keep: en_GB, en_US, fr_FR

$keepLanguages = @("en_GB", "en_US", "fr_FR")
$localeDir = "thonny\locale"

Write-Host "Removing unused language folders from Thonny..."
Write-Host ""

$removed = 0
$kept = 0

Get-ChildItem $localeDir -Directory | ForEach-Object {
    if ($keepLanguages -contains $_.Name) {
        Write-Host "KEEP: $($_.Name)" -ForegroundColor Green
        $kept++
    } else {
        Write-Host "REMOVE: $($_.Name)" -ForegroundColor Yellow
        Remove-Item $_.FullName -Recurse -Force
        $removed++
    }
}

Write-Host ""
Write-Host "Summary:"
Write-Host "  Kept: $kept languages" -ForegroundColor Green
Write-Host "  Removed: $removed languages" -ForegroundColor Yellow
