import socket
import time
from config  import create_packet, get_auth_hash
from config import parse_packet

def send_file_rudp(filename, server_addr):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.5) # Timeout para retransmissão [cite: 25]
    
    seq_num = 0
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(1024) # Tamanho do bloco
            if not chunk: break
            
            packet = create_packet(seq_num, chunk)
            
            # Loop de retransmissão (Stop-and-Wait) [cite: 12]
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