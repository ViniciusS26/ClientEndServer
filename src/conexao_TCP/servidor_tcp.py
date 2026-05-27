import hashlib
from http import server
import socket
import threading
from urllib import request

bind_ip = "95.58.0.3"
bind_port = 80

MATRICULA = "20219027928"
NOME = "VINICIUS DA SILVA NUNES"

def gera_hash_esperado():
    """Gera o Hash SHA-256 esperado para comparação"""
    payload = MATRICULA + NOME
    print(f"[*] Gerando hash esperado para payload: {payload}")
    return hashlib.sha256(payload.encode()).digest()

def hash_valida(recebido):
    """Verifica se o hash recebido é válido comparando com o hash esperado"""
    hash_esperado = gera_hash_esperado()
    print(f"[*] Hash recebido: {recebido.hex()}")
    print(f"[*] Hash esperado: {hash_esperado.hex()}")
    return recebido == hash_esperado

class ServidorTCP:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.ip, self.port))
        self.servidor.listen(5)
        print(f"[*] Servidor TCP iniciado em {self.ip}:{self.port}")
    

    def handle_client(self, client_socket):
        mensagemRecibda = client_socket.recv(1024)
        print(f"[*] Requsição recebida: {mensagemRecibda.decode()}")
        
        if mensagemRecibda.startswith(b"X-Custom-Auth: "):
            hash_recebido = bytes.fromhex(mensagemRecibda[len(b"X-Custom-Auth: "):].strip().decode())
            if hash_valida(hash_recebido):
                print("[*] Hash válido recebido. Enviando resposta de sucesso.")
                client_socket.send(f"Hash válido! Acesso concedido.".encode())
            else:
                print("[*] Hash inválido recebido. Enviando resposta de falha.")
                client_socket.send(f"Hash inválido! Acesso negado.")
        else:
            print("[*] Requisição sem campo X-Custom-Auth. Enviando resposta de erro.")
            client_socket.send(f"Requisição inválida! Campo X-Custom-Auth ausente.".encode())
        client_socket.send(b"ACK Recebido de " + client_socket.getpeername()[0].encode() + b"!")
        client_socket.close()

    def start_server(self):
        while True:
            client, addr = self.servidor.accept()
            print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()



if __name__ == "__main__":    
    servidor = ServidorTCP(bind_ip, bind_port)
    servidor.start_server()