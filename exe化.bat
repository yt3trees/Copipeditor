echo off
echo %~dp0
echo 事前にpip install cx_Freezeでcs_Freezeをインストールしてください。
echo buildフォルダ内にexeが格納されます。
python setup.py build
echo その他のファイルをまとめてappに格納します。
if exist .\app\FileCopy\FileCopy.exe (
    echo 上書きします。
    echo A | xcopy .\build\exe.win-amd64-3.9 .\app\FileCopy /S
) else (
    echo 新規でコピーします。
    echo D | xcopy .\build\exe.win-amd64-3.9 .\app\FileCopy /S
)
rem echo A | xcopy .\script .\app\FileCopy\script /S
rem echo A | xcopy .\script\run_スタートメニューに追加.bat .\app\FileCopy /S
if exist .\app\FileCopy\script (
    echo 上書きします。
    echo A | xcopy .\script .\app\FileCopy\script /S
) else (
    echo 新規でコピーします。
    echo D | xcopy .\script .\app\FileCopy\script /S
)
pause