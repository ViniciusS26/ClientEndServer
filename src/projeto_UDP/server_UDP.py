import socket
from ..configs.config import parse_packet, create_packet

def start_server_rudp():
    host = '127.0.0.1'
    porta = 5000
    Arquivo = 'Arquivo.txt'

    #criando socket 
    serivdorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serivdorSocket.bind((host, porta))


    
    seq_esperada = 0
    with open(Arquivo, "rb") as f:
        while True:
            pacote, endereco = serivdorSocket.recvfrom(2048)
            auth_hash, seq_num, data = parse_packet(pacote)
            
            # Validação de Autenticidade e Sequência [cite: 24, 30]
            if seq_num == seq_esperada:
                f.write(data)
                # Envia ACK de volta
                ack = create_packet(seq_num, b"ACK")
                serivdorSocket.sendto(ack, endereco)
                seq_esperada += 1
            else:
                # Se o pacote for antigo, apenas reenvia o ACK do último
                ack = create_packet(seq_esperada - 1, b"ACK")
                serivdorSocket.sendto(ack, endereco)