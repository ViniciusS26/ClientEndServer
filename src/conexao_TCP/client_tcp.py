import hashlib
import socket
from time import time

target_host = "95.58.0.3"
target_port = 80
MATRICULA = "20219027928"
NOME = "VINICIUS DA SILVA NUNES"

class CustomAuth:
    def __init__(self, matricula, nome):
        self.matricula = matricula
        self.nome = nome

    def get_auth_hash(self):
        """Gera o Hash SHA-256 para o campo X-Custom-Auth"""
        payload = self.matricula + self.nome
        print(f"[*] Gerando hash para payload: {payload}")
        return hashlib.sha256(payload.encode()).digest()

X_CUSTOM_AUTH = CustomAuth(MATRICULA, NOME).get_auth_hash()
numero_requisicao = 5
numero_execucao = 10

class ClientTCP:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def enviar_requisicao(self):
        """Envia uma requisição TCP para o servidor com o campo X-Custom-Auth"""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))
        mensagem = f"X-Custom-Auth: {X_CUSTOM_AUTH.hex()}"
        print(f"[*] Enviando requisição: {mensagem}")
        client.send(mensagem.encode())
        response = client.recv(1024)
        print(f"[*] Resposta recebida: {response}")
        client.close()




if __name__ == "__main__":
    Clente = ClientTCP(target_host, target_port)
    for i in range(numero_execucao):
        print(f"[*] Enviando requisição {i+1}/{numero_execucao}")
        start_time = time()
        for _ in range(numero_requisicao):
            Clente.enviar_requisicao()
        end_time = time()
        print(f"[*] Tempo total para {numero_requisicao} requisições: {end_time - start_time:.2f} segundos\n")
    