echo off
echo %~dp0
echo ���O��pip install cx_Freeze��cs_Freeze���C���X�g�[�����Ă��������B
echo build�t�H���_����exe���i�[����܂��B
python setup.py build
echo ���̑��̃t�@�C�����܂Ƃ߂�app�Ɋi�[���܂��B
if exist .\app\FileCopy\FileCopy.exe (
    echo �㏑�����܂��B
    echo A | xcopy .\build\exe.win-amd64-3.9 .\app\FileCopy /S
) else (
    echo �V�K�ŃR�s�[���܂��B
    echo D | xcopy .\build\exe.win-amd64-3.9 .\app\FileCopy /S
)
rem echo A | xcopy .\script .\app\FileCopy\script /S
rem echo A | xcopy .\script\run_�X�^�[�g���j���[�ɒǉ�.bat .\app\FileCopy /S
if exist .\app\FileCopy\script (
    echo �㏑�����܂��B
    echo A | xcopy .\script .\app\FileCopy\script /S
) else (
    echo �V�K�ŃR�s�[���܂��B
    echo D | xcopy .\script .\app\FileCopy\script /S
)
pause