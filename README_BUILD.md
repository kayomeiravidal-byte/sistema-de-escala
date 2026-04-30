# Guía Completa: Empaquetar Aplicación Django para Windows (.exe)

Este documento fornece o passo a passo completo para gerar um executável .exe para Windows a partir do seu projeto Python/Django.

## 📋 Estrutura do Projeto

```
projeto/
├── main.py                 # Entry point (servidor + navegador)
├── main.spec               # Configuração PyInstaller
├── requirements.txt        # Dependências
├── db.sqlite3             # Banco de dados SQLite
├── scheduling_system/      # Projeto Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shifts/                # App Django
│   ├── models.py
│   ├── views.py
│   └── ...
└── build.bat              # Script de build (Windows)
```

---

## 🔧 Passo 1: Instalação do Python no Windows

### 1.1 Download
Acesse: https://www.python.org/downloads/

Baixe **Python 3.11.x** ou **3.12.x** (versões stable mais recentes)

### 1.2 Instalação
1. Execute o instalador `.exe`
2. **⚠️ IMPORTANTE**: Marque a opção **"Add Python to PATH"**
3. Escolha "Customize installation"
4. Marque todas as opções(opcional)
5. INSTALE!

### 1.3 Verificar Instalação
Abra o terminal (cmd ou PowerShell):
```powershell
python --version
pip --version
```

---

## 📦 Passo 2: Instalar Dependências

### 2.1 Criar Ambiente Virtual (Recomendado)
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate
```

### 2.2 Instalar Dependências do Projeto
```powershell
pip install -r requirements.txt
```

### 2.3 Instalar PyInstaller
```powershell
pip install pyinstaller
```

### 2.4 Verificar PyInstaller
```powershell
pyinstaller --version
```

---

## ⚙️ Passo 3: Configurar o main.py

O arquivo `main.py` foi atualizado com as seguintes melhorias:

✅ Porta fixa **5000**
✅ Abre navegador automaticamente
✅ Evita abas duplicadas (verifica se já está aberto)
✅ Tratamento de erros melhorado

---

## 🏗️ Passo 4: Gerar o Executável (.exe)

### Método 1: Usando o build.bat (Recomendado)

1. Copie o arquivo `build.bat` para a raiz do projeto
2. Execute no terminal (como Administrador):
```powershell
build.bat
```

### Método 2: Usando PyInstaller diretamente

```powershell
pyinstaller main.spec --clean
```

### Método 3: Comandos manuais (alternativo)

```powershell
# Limpar builds anteriores
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

# Criar o executável
pyInstaller main.py ^
    --onefile ^
    --name "ServidorAgenda" ^
    --add-data "db.sqlite3;." ^
    --hidden-import=django ^
    --hidden-import=djangorestframework ^
    --hidden-import=waitress ^
    --hidden-import=pandas ^
    --hidden-import=ortools ^
    --collect-all django ^
    --collect-all djangorestframework ^
    --console ^
    --clean
```

---

## 📁 Passo 5: Estrutura Final de Arquivos

Após a construção, você terá:

```
dist/
└── ServidorAgenda.exe    # ✅ Executável pronto!
```

### Arquivos necessários para distribuição:
```
dist/
├── ServidorAgenda.exe    # Executável principal
└── db.sqlite3           # Banco de dados (copiar se necessário)
```

---

## 🚀 Como Rodar o Executável

### No Windows (sem Python instalado):

1. Copie `ServidorAgenda.exe` para uma pasta
2. (Opcional) Copie `db.sqlite3` se existir
3. Execute o `.exe`
4. O servidor inicia na porta **5000**
5. Navegador abre automaticamente: http://localhost:5000

---

## ❌ Erros Comuns e Soluções

### Erro 1: Antivírus detecta como malware
**Sintoma**: Arquivo apagado ou em quarentena

**Solução**:
1. Adicione exclusão no antivírus
2. Assine digitalmente (para distribuição)
3. Use certificado EV (opcional)

### Erro 2: Porta já em uso
**Sintoma**: `OSError: [WinError 10048]`

**Solução**:
```powershell
# Verificar processos na porta
netstat -ano | findstr :5000

# Matar processo
taskkill /PID <PID> /F
```

alternativamente, mude a porta no código.

### Erro 3: Dependências faltando
**Sintoma**: `ModuleNotFoundError`

**Solução**:
1. Atualize o `--hidden-imports` no `.spec`
2. Use `--collect-all` para pacotes grandes
3. Reconstrua o executável

### Erro 4: Banco de dados não encontrado
**Sintoma**: Erro ao acessar SQLite

**Solução**:
1. Configure o caminho corretamente no settings.py
2. Use caminhos absolutos para produção

### Erro 5: PyInstaller não funciona
**Sintoma**: Erro na geração

**Solução**:
```powershell
# Atualize pip e pyinstaller
pip install --upgrade pip pyinstaller

# Limpe e reconstrua
pyinstaller --clean
```

---

## 🔄 GitHub Actions (Build Automático)

O workflow em `.github/workflows/build.yml` faz:

1. Trigger: a cada push na branch `main`
2. Instala Python no runner do GitHub
3. Instala dependências
4. Executa PyInstaller
5. Disponibiliza o .exe como artefato para download

### Como usar:
1. Faça push do código para o GitHub
2. Vá em **Actions** no repositório
3. Clique no workflow executado
4. Baixe o artefato em **Artifacts**

---

## 📞 Suporte

Se tiver problemas:
1. Verifique Python versão: `python --version`
2. Verifique pip: `pip list`
3. Teste execução direta: `python main.py`
4. Verifique logs do PyInstaller

---

## ✅ Checklist Pré-Build

- [ ] Python 3.11+ instalado no Windows
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] PyInstaller instalado (`pip install pyinstaller`)
- [ ] Teste execução direta funciona (`python main.py`)
- [ ] Arquivo `main.spec` configurado corretamente
- [ ] build.bat copiado para pasta do projeto

---

**Data de criação**: 2025
**Autor**: blackboxai
