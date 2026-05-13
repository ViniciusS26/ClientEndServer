import socket
from config import parse_packet, create_packet

def start_server_rudp(ip="0.0.0.0", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    
    expected_seq = 0
    with open("received_file.bin", "wb") as f:
        while True:
            packet, addr = server_socket.recvfrom(2048)
            auth_hash, seq_num, data = parse_packet(packet)
            
            # Validação de Autenticidade e Sequência [cite: 24, 30]
            if seq_num == expected_seq:
                f.write(data)
                # Envia ACK de volta
                ack = create_packet(seq_num, b"ACK")
                server_socket.sendto(ack, addr)
                expected_seq += 1
            else:
                # Se o pacote for antigo, apenas reenvia o ACK do último
                ack = create_packet(expected_seq - 1, b"ACK")
                server_socket.sendto(ack, addr)