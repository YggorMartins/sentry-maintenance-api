@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [1/4] Validando ferramentas...
where npm >nul 2>nul || (echo ERRO: npm nao encontrado no PATH. & exit /b 1)
where pyinstaller >nul 2>nul || (echo ERRO: PyInstaller nao encontrado. Execute: pip install -r requirements-desktop.txt & exit /b 1)

echo [2/4] Compilando o frontend React...
pushd frontend
call npm run build
if errorlevel 1 (popd & echo ERRO: falha no build do frontend. & exit /b 1)
popd

echo [3/4] Copiando frontend\dist para app\static...
if exist "app\static" rmdir /s /q "app\static"
mkdir "app\static"
xcopy "frontend\dist\*" "app\static\" /E /I /Y /Q >nul
if errorlevel 1 (echo ERRO: falha ao copiar os arquivos estaticos. & exit /b 1)

echo [4/4] Gerando executavel Windows com PyInstaller...
pyinstaller --noconfirm --onedir --windowed --add-data "app/static;app/static" --name "SentryMaintenance" main_desktop.py
if errorlevel 1 (echo ERRO: falha ao gerar o executavel. & exit /b 1)

echo.
echo Build concluido: dist\SentryMaintenance\SentryMaintenance.exe
exit /b 0
