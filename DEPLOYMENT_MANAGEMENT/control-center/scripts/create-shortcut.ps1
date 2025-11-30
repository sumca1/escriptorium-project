# Create Desktop Shortcut for Terminal Server
# ==========================================

$scriptPath = "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\scripts\utilities\auto-start-terminal-server.ps1"
$vbsPath = "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\start-servers.vbs"

# בדוק אם VBS קיים
if (Test-Path $vbsPath) {
    Write-Host "✅ שימוש ב-VBScript launcher" -ForegroundColor Green
    $targetPath = $vbsPath
    $iconLocation = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
} else {
    Write-Host "⚠️ VBS לא נמצא, שימוש ישיר ב-PowerShell" -ForegroundColor Yellow
    $targetPath = "pwsh.exe"
    $iconLocation = "C:\Program Files\PowerShell\7\pwsh.exe"
}

# יצירת קיצור דרך
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Start Terminal Server.lnk"

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)

if ($targetPath -like "*.vbs") {
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"$vbsPath`""
} else {
    $shortcut.TargetPath = $targetPath
    $shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$scriptPath`" -NoBrowser"
}

$shortcut.WorkingDirectory = "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset"
$shortcut.Description = "Start Terminal Server + Dashboard Server"
$shortcut.IconLocation = $iconLocation

$shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ קיצור דרך נוצר בהצלחה!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 מיקום: $shortcutPath" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 כעת תוכל:" -ForegroundColor Yellow
Write-Host "   1. לפתוח את השרתים בלחיצה כפולה על הקיצור בדסקטופ" -ForegroundColor White
Write-Host "   2. להעתיק את start-servers.vbs לכל מקום ולהפעיל אותו" -ForegroundColor White
Write-Host ""
