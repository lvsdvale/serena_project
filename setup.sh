#!/bin/bash

# Nome do ambiente Conda
ENV_NAME="serena_env"

# Verifica se o conda está instalado
if ! command -v conda &> /dev/null; then
    echo "Conda não encontrado. Por favor, instale o Miniconda ou Anaconda primeiro."
    exit 1
fi

# Verifica se o ambiente já existe
if conda env list | grep -qE "^$ENV_NAME\s"; then
    echo "O ambiente Conda '$ENV_NAME' já existe. Pulando a criação."
else
    # Criação do ambiente com Python 3.9.7
    echo "Criando o ambiente Conda '$ENV_NAME' com Python 3.9.7..."
    conda create -y -n $ENV_NAME python=3.9.7
fi

# Ativando o ambiente
echo "Ativando o ambiente Conda..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Instala os pacotes do requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Instalando pacotes do requirements.txt..."
    pip install -r requirements.txt
else
    echo "Arquivo requirements.txt não encontrado!"
    exit 1
fi

# Instala o pre-commit
echo "Instalando pre-commit..."
pip install pre-commit

# Instala os hooks definidos em .pre-commit-config.yaml
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Configurando pre-commit hooks..."
    pre-commit install
else
    echo "Arquivo .pre-commit-config.yaml não encontrado!"
    exit 1
fi

echo "Ambiente '$ENV_NAME' configurado com sucesso!"
