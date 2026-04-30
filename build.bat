@echo off
REM ============================================================
REM build.bat - Script para gerar o .exe no Windows
REM 
REM Como usar:
REM 1. Abra o terminal como Administrador
REM 2. Execute: build.bat
REM ============================================================

echo.
echo ============================================================
echo  🎯 Build doServidorAgenda para Windows
echo ============================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não encontrado!
    echo.
    echo Por favor,instale o Python primeiro:
    echo   https://www.python.org/downloads/
    echo.
    echo Depois,insteale novamente este script.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verifica se pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: pip não encontrado!
    pause
    exit /b 1
)

echo ✅ pip encontrado

REM Instala/atualiza dependências
echo.
echo 📦 Instalando dependências...
echo.

pip install --upgrade pip >nul 2>&1

REM Instala dependências do projeto
echo 📦 Instalando dependências do projeto...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências!
    pause
    exit /b 1
)

echo ✅ Dependências instaladas

REM Instala PyInstaller
echo 📦 Instalando PyInstaller...
pip install pyinstaller

if errorlevel 1 (
    echo ❌ Erro ao instalar PyInstaller!
    pause
    exit /b 1
)

echo ✅ PyInstaller instalado

REM Limpa builds anteriores
echo.
echo 🧹 Limpando builds anteriores...
echo.

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist scheduling_system\__pycache__ rmdir /s /q scheduling_system\__pycache__
if exist shifts\__pycache__ rmdir /s /q shifts\__pycache__

echo ✅ Limpeza concluída

REM Cria o executável usando o arquivo .spec
echo.
echo 🏗️  Gerando o executável...
echo.

pyinstaller main.spec --clean

if errorlevel 1 (
    echo ❌ Erro ao gerar o executável!
    echo.
    echo Verifique os erros acima e tente novamente.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  ✅ Build concluído com sucesso!
echo ============================================================
echo.
echo 📁 Executável gerado em:
echo    dist\ServidorAgenda.exe
echo.
echo 📋 Estrutura:
echo    - dist\ServidorAgenda.exe  (executável)
echo    - db.sqlite3                (banco de dados, se existir)
echo.
echo ▶️ Como executar:
echo    1. Copie o arquivo .exe para a pasta desejada
echo    2. Execute o .exe
echo    3. O navegadorabrirá automaticamente
echo    4. Acesse: http://localhost:5000
echo.
echo ============================================================

pause
