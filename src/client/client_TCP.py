import socket
import time
import hashlib
import struct

NOME = "Vinicius da Silva Nunes"
MATRICULA = "20219027928"

def get_auth_hash():
    """Gera o Hash SHA-256 para o campo X-Custom-Auth [cite: 30]"""
    payload = MATRICULA + NOME
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



def send_file_rudp(filename, server_addr):
    print(f"Enviando {filename} para {server_addr} usando RUDP...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.5) # Timeout para retransmissão 
    
    seq_num = 0
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(1024) # Tamanho do bloco
            if not chunk: 
                break
            
            packet = create_packet(seq_num, chunk)
            
            # Loop de retransmissão (Stop-and-Wait)
            while True:
                try:
                    client_socket.sendto(packet, server_addr)
                    # Espera pelo ACK
                    ack_packet, _ = client_socket.recvfrom(64)
                    _, ack_seq, _ = parse_packet(ack_packet)
                    
                    if ack_seq == seq_num:
                        print(f"Bloco {seq_num} confirmado!")
                        seq_num += 1
                        break
                except socket.timeout:
                    print(f"Timeout! Reenviando bloco {seq_num}...")
    
    client_socket.close()



if __name__ == "__main__":
    """ Realiza testes de envio do arquivo usando RUDP """
    server_address = ('127.0.0.1', 8000)
    send_file_rudp("Arquivo.txt", server_address)
