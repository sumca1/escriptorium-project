Set WshShell = CreateObject("WScript.Shell")

' הפעלת auto-start-terminal-server.ps1 בחלון PowerShell חדש
scriptPath = "i:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\escriptorium\ui\control-center\scripts\utilities\auto-start-terminal-server.ps1"

' פקודה: פתח PowerShell עם הסקריפט
command = "pwsh.exe -NoExit -ExecutionPolicy Bypass -File """ & scriptPath & """ -NoBrowser"

' הרץ את הפקודה (1 = חלון רגיל, True = המתן לסיום)
WshShell.Run command, 1, False

' הצג הודעה
MsgBox "Terminal Server מופעל!" & vbCrLf & vbCrLf & "חלון PowerShell נפתח עם השרתים.", 64, "מרכז הבקרה"

Set WshShell = Nothing
