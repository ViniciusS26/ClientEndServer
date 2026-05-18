FROM ubuntu:22.04

# Evita prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala Python, ferramentas de rede e compiladores necessários
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iproute2 \
    tcpdump \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Instala Pandas e Matplotlib para a parte de análise estatística
RUN pip3 install pandas matplotlib

# Define o diretório de trabalho
WORKDIR /app

# O comando padrão mantém o container vivo para executarmos os testes
CMD  ["python3", "client/client_TCP.py"]