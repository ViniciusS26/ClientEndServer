import socket
import threading

bind_ip = "127.0.0.1"
bind_port = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)
print(f"[*] Servidor ouvindo na porta: {bind_ip}:{bind_port}")

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print(f"[*] Requsição recebida: {request}")

    client_socket.send(b"ACK Recebido!")
    client_socket.close()


def start_server():
    while True:
        client, addr = server.accept()
        print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":    
    start_server()