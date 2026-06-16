"""Entrypoint serverless do Vercel — expõe a aplicação WSGI do Django."""
import os
import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path para importar o pacote Django.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scheduling_system.settings")

from scheduling_system.wsgi import application

# O runtime Python do Vercel procura uma variável WSGI chamada `app`.
app = application
