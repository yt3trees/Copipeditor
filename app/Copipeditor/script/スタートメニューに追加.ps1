Write-Host スタートメニューにアプリを追加します。
$rd = Read-Host "追加しますか？(y/n)"
if ($rd -eq "y"){
    Set-Location $PSScriptRoot
    Set-Location ..
    $str_path = (Convert-Path .)
    $WsShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WsShell.CreateShortcut("$str_path\Copipeditor.lnk")
    $Shortcut.TargetPath = "$str_path\Copipeditor.exe"
    $Shortcut.IconLocation = "$str_path\Copipeditor.exe"
    $Shortcut.Save()
    $a = [Environment]::GetFolderPath('CommonPrograms')
    Move-Item "$str_path\Copipeditor.lnk" "$a\Copipeditor.lnk" -Force
    Write-Host 追加しました。`r`n※追加後exeファイルの場所を移動した場合は再度実行し直してください。
}
else {
    Write-Host 処理を中止しました。
}