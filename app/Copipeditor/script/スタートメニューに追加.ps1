Write-Host �X�^�[�g���j���[�ɃA�v����ǉ����܂��B
$rd = Read-Host "�ǉ����܂����H(y/n)"
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
    Write-Host �ǉ����܂����B`r`n���ǉ���exe�t�@�C���̏ꏊ���ړ������ꍇ�͍ēx���s�������Ă��������B
}
else {
    Write-Host �����𒆎~���܂����B
}