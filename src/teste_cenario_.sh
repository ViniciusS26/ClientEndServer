#!/bin/bash

# Verifica se o script está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute este script como root ou usando sudo."
  exit 1
fi

INTERFACE="eth0"
CENARIO=$(echo "$1" | tr '[:lower:]' '[:upper:]')

# Função para limpar regras existentes
limpar_regras() {
    echo "Limpando configurações de rede anteriores em $INTERFACE..."
    tc qdisc del dev $INTERFACE root 2>/dev/null
}

case $CENARIO in
    A)
        limpar_regras
        echo "Aplicando Cenário A: 0% de perda / 10ms de delay"
        # Como o padrão é 0% de perda, basta aplicar o delay
        tc qdisc add dev $INTERFACE root netem delay 10ms
        ;;
    B)
        limpar_regras
        echo "Aplicando Cenário B: 5% de perda / 50ms de delay"
        tc qdisc add dev $INTERFACE root netem delay 50ms loss 5%
        ;;
    C)
        limpar_regras
        echo "Aplicando Cenário C: 10% de perda / 100ms de delay"
        tc qdisc add dev $INTERFACE root netem delay 100ms loss 10%
        ;;
    LIMPAR|CLEAN)
        limpar_regras
        echo "Rede restaurada para o estado padrão (sem latência ou perdas)."
        ;;
    *)
        echo "Uso: $0 {A|B|C|limpar}"
        echo "  A      : 0% perda / 10ms delay"
        echo "  B      : 5% perda / 50ms delay"
        echo "  C      : 10% perda / 100ms delay"
        echo "  limpar : Remove qualquer limitação aplicada"
        exit 1
        ;;
esac

# Exibe o status atual da interface para validação
echo -e "\n--- Status Atual da Interface $INTERFACE ---"
tc qdisc show dev $INTERFACE