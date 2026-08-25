$TaskName = "KgamjaBlogAutoPost"
$BatPath = "C:\Users\dlwod\.gemini\antigravity\scratch\kgamja_auto_blog\run_auto_post.bat"
$WorkingDir = "C:\Users\dlwod\.gemini\antigravity\scratch\kgamja_auto_blog"

# 기존 작업 해제
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 하루 4회 실행 트리거 (09:00, 12:00, 17:00, 20:00)
$Triggers = @(
    (New-ScheduledTaskTrigger -Daily -At "09:00"),
    (New-ScheduledTaskTrigger -Daily -At "12:00"),
    (New-ScheduledTaskTrigger -Daily -At "17:00"),
    (New-ScheduledTaskTrigger -Daily -At "20:00")
)

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $WorkingDir
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Trigger $Triggers -Action $Action -Settings $Settings -Description "kgamjablog.blog daily auto posting at 09:00, 12:00, 17:00, 20:00"

Write-Output "Successfully updated Windows Scheduled Task: $TaskName (Daily 4 times: 09:00, 12:00, 17:00, 20:00)"
