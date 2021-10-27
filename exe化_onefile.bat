rem upx --upx-dir C:\upx-3.96-win64
pyinstaller Copipeditor.py --name Copipeditor --onefile --icon=icon/copytool.ico

if exist .\app\Copipeditor\Copipeditor.exe (
    echo 上書きします。
    echo A | xcopy .\dist .\app\Copipeditor /S
) else (
    echo 新規でコピーします。
    echo D | xcopy .\dist .\app\Copipeditor /S
)
pause