import socket

import hashlib
import struct

NOME = "Vinicius da Silva Nunes"
MATRICULA = "20219027928"

def get_auth_hash():
    """Gera o Hash SHA-256 para o campo X-Custom-Auth [cite: 30]"""
    payload = MATRICULA + NOME
    print(f"Payload para hash: {payload}")
    return hashlib.sha256(payload.encode()).digest()

def create_packet(seq_num, data):
    """
    Estrutura: [Hash(32 bytes)] + [Seq(4 bytes)] + [Payload]
    Total de overhead: 36 bytes [cite: 57, 58]
    """
    header = struct.pack("!32sI", get_auth_hash(), seq_num)
    return header + data

def parse_packet(packet):
    """Desempacota o cabeçalho e retorna (hash, seq, data)"""
    header_size = 36
    header = packet[:header_size]
    data = packet[header_size:]
    auth_hash, seq_num = struct.unpack("!32sI", header)
    return auth_hash, seq_num, data

def start_server_rudp():
    host = '127.0.0.1'
    porta = 80
    Arquivo = './Arquivo.txt'

    #criando socket 
    serivdorSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serivdorSocket.bind((host, porta))
    serivdorSocket.listen(10)  # Escuta por conexões

    expected_seq = 0
    while True:
            client_socket, addr = serivdorSocket.accept()
            packet = client_socket.recv(2048)
            auth_hash, seq_num, data = parse_packet(packet)
            print(f"Recebido pacote {seq_num} de {addr}")
            # Validação de Autenticidade e Sequência 
            if seq_num == expected_seq:
                with open(Arquivo, "ab") as f:
                    f.write(data)
                # Envia ACK de volta
                ack = create_packet(seq_num, b"ACK")
                client_socket.send(ack)
                expected_seq += 1
            else:
                # Se o pacote for antigo, apenas reenvia o ACK do último
                ack = create_packet(expected_seq - 1, b"ACK")
                client_socket.send(ack)



if __name__ == "__main__":
    start_server_rudp()