@echo off
REM ============================================================
REM installer.bat - Instalador Automático Completo
REM 
REM Este script:
REM 1. Instala Python automaticamente se não existir
REM 2. Instala todas as dependências automáticamente
REM 3. Executa o servidor
REM 
REM O cliente NÃO precisa instalar nada manualmente!
REM Apenas execute este arquivo!
REM ============================================================

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo.
echo ============================================================
echo  🎯 Instalador Automático - Servidor Agenda
echo ============================================================
echo.

REM Verifica se já tem Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python já instalado:
    python --version
    goto :install_dependencies
)

echo 🔄 Python não encontrado. Instalando automaticamente...
echo.

REM Detecta arquitetura do Windows
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "ARCH=amd64"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
) else (
    set "ARCH=32"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe"
)

echo 📥 Baixando Python 3.11...
echo    Arquitetura: %ARCH%
echo.

REM Baixa Python (usando curl ou powershell)
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP%\python-installer.exe'"

if not exist "%TEMP%\python-installer.exe" (
    echo ❌ Erro ao baixar Python
    echo Tentando método alternativo...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe' -OutFile '$env:TEMP\python-installer.exe'}"
)

if not exist "%TEMP%\python-installer.exe" (
    echo ❌ Erro ao baixar Python
    echo.
    echo Por favor, instale Python manualmente:
    echo    https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ⚙️  Instalando Python (aguarde)...
echo.

REM Instala Python silenciosamente
"%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar Python
    echo Codigo de erro: %errorlevel%
    pause
    exit /b 1
)

echo ✅ Python instalado com sucesso!
echo.

REM Limpa instalador
del "%TEMP%\python-installer.exe" 2>nul

REM Aguarda Python estar disponível
echo ⏳ Aguardando Python ficar disponível...
:wait_python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 /nobreak >nul
    goto :wait_python
)

echo ✅ Python disponível:
python --version
echo.

:install_dependencies
echo.
echo ============================================================
echo  📦 Instalando Dependências
echo ============================================================
echo.

REM Atualiza pip
python -m pip install --upgrade pip --quiet

REM Instala dependências do projeto
echo 📦 Instalando dependências do projeto...

REM Verifica se requirements.txt existe
if exist "%PROJECT_DIR%\requirements.txt" (
    python -m pip install -r "%PROJECT_DIR%\requirements.txt" --quiet
) else (
    echo 📦 Instalando dependências padrão...
    python -m pip install django djangorestframework waitress pandas --quiet
)

if %errorlevel% neq 0 (
    echo ⚠️  Erro ao instalar algumas dependências
    echo    Tentando continuar...
)

echo ✅ Dependências instaladas!

REM Verifica se precisa gerar o executável
if exist "%PROJECT_DIR%\dist\ServidorAgenda.exe" (
    echo.
    echo ============================================================
    echo  ▶️  Executando Servidor...
    echo ============================================================
    echo.
    echo    URL: http://localhost:5000
    echo    Navegador abrindo automaticamente...
    echo.
    
    cd /d "%PROJECT_DIR%\dist"
    start ServidorAgenda.exe
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
    goto :end
)

echo.
echo ============================================================
echo  ⚙️  Gerando Executável
echo ============================================================
echo.

REM Instala PyInstaller
python -m pip install pyinstaller --quiet

REM Gera o executável
cd /d "%PROJECT_DIR%"
pyinstaller main.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo ❌ Erro ao gerar executável
    echo Tentando método alternativo...
    pyinstaller main.py --onefile --name ServidorAgenda --console --clean
)

echo.
echo ============================================================
echo  ▶️  Executando Servidor...
echo ============================================================
echo.
echo    URL: http://localhost:5000
echo    Navegador abrindo automaticamente...
echo.

REM Executa o servidor
if exist "dist\ServidorAgenda.exe" (
    cd /d "%PROJECT_DIR%\dist"
    start ServidorAgenda.exe
) else (
    cd /d "%PROJECT_DIR%"
    start python main.py
)

timeout /t 3 /nobreak >nul
start http://localhost:5000

:end
echo.
echo ============================================================
echo  ✅ Tudo Pronto!
echo ============================================================
echo.
echo    O servidor está rodando!
echo    Acesse: http://localhost:5000
echo.
echo    Este instalador criou:
echo    - Python (se necessário)
echo    - Dependências
echo    - Executável
echo.
echo    Para próxima vez, use:
echo    dist\ServidorAgenda.exe
echo.

pause
