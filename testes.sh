#!/bin/bash

# Configurações de Cenário (Exemplo Cenário C: 10% perda / 100ms delay)
# [cite: 39]
DELAY="100ms"
LOSS="10%"

echo "Configurando rede no container do cliente..."
docker exec -it redes_client tc qdisc add dev eth0 root netem delay $DELAY loss $LOSS

echo "Iniciando bateria de 20 testes..."

for i in {1..20}
do
   echo "Execução $i..."
   # Inicia captura em background no servidor
   docker exec -d redes_server tcpdump -i eth0 -w /app/captures/teste_$i.pcap
   
   # Executa o cliente (ajuste os argumentos conforme seu código)
   docker exec -it redes_client python3 client.py --modo rudp --arquivo teste.bin
   
   # Para o tcpdump
   docker exec -it redes_server pkill tcpdump
done

echo "Testes concluídos. Removendo regras de rede..."
docker exec -it redes_client tc qdisc del dev eth0 root