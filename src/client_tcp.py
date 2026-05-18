import socket

target_host = "127.0.0.1"
target_port = 8080


def start_client():
    num_requests = 5
   
    while num_requests > 0:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((target_host, target_port))
        client.send("Olá, servidor TCP!".encode())
        response = client.recv(1024)
        print(f"[*] Resposta recebida: {response}")
        num_requests -= 1

        client.close()


if __name__ == "__main__":
    start_client()