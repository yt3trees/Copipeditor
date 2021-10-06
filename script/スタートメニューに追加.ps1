Write-Host スタートメニューにアプリを追加します。
$rd = Read-Host "追加しますか？(y/n)"
if ($rd -eq "y"){
    Set-Location $PSScriptRoot
    Set-Location ..
    $str_path = (Convert-Path .)
    $WsShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WsShell.CreateShortcut("$str_path\FileCopy.lnk")
    $Shortcut.TargetPath = "$str_path\FileCopy.exe"
    $Shortcut.IconLocation = "$str_path\FileCopy.exe"
    $Shortcut.Save()
    $a = [Environment]::GetFolderPath('CommonPrograms')
    Move-Item "$str_path\FileCopy.lnk" "$a\FileCopy.lnk" -Force
    Write-Host 追加しました。`r`n※追加後exeファイルの場所を移動した場合は再度実行し直してください。
}
else {
    Write-Host 処理を中止しました。
}