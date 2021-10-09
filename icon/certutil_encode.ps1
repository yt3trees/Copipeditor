if (Test-Path copytool.txt) {
    Remove-Item -Path copytool.txt
}
certutil -encode copytool.gif copytool.txt
pause