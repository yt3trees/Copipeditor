Write-Host �X�^�[�g���j���[�ɃA�v����ǉ����܂��B
$rd = Read-Host "�ǉ����܂����H(y/n)"
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
    Write-Host �ǉ����܂����B`r`n���ǉ���exe�t�@�C���̏ꏊ���ړ������ꍇ�͍ēx���s�������Ă��������B
}
else {
    Write-Host �����𒆎~���܂����B
}