import hashlib
import os
import socket
from time import time

target_host = "95.58.0.3"
target_port = 80
MATRICULA = "20219027928"
NOME = "VINICIUS DA SILVA NUNES"

# Pasta local onde o cliente vai salvar os arquivos baixados
PASTA_DOWNLOADS = "./downloads_cliente"


class CustomAuth:

    def __init__(self, matricula, nome):
        self.matricula = matricula
        self.nome = nome

    def get_auth_hash(self):
        """Gera o Hash SHA-256 para o campo X-Custom-Auth"""
        payload = self.matricula + self.nome
        return hashlib.sha256(payload.encode()).digest()


X_CUSTOM_AUTH = CustomAuth(MATRICULA, NOME).get_auth_hash()


class ClientTCP:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Garante que a pasta de downloads exista no lado do cliente
        if not os.path.exists(PASTA_DOWNLOADS):
            os.makedirs(PASTA_DOWNLOADS)

    def solicitar_arquivo(self, nome_arquivo):
        """Solicita um arquivo ao servidor e faz o download em blocos"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))

            # Monta a requisição formatada com a quebra de linha \n separando o hash do nome do arquivo
            requisicao = (f"X-Custom-Auth: {X_CUSTOM_AUTH.hex()}\n{nome_arquivo}")
            client.send(requisicao.encode())

            # Recebe o cabeçalho de resposta (Ex: b"OK|1024\n" ou mensagem de erro)
            resposta_inicial = client.recv(1024)

            if resposta_inicial.startswith(b"OK|"):
                # Extrai o tamanho do arquivo enviado pelo servidor
                dados_header = resposta_inicial.decode().strip().split("|")
                tamanho_arquivo = int(dados_header[1])
                caminho_salvar = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
                bytes_recebidos = 0

                # Abre o arquivo local para escrita binária ('wb')
                with open(caminho_salvar, "wb") as f:
                    while bytes_recebidos < tamanho_arquivo:
                        # Lê em blocos de até 4KB
                        chunk = client.recv(4096)
                        if not chunk:
                            break  # Conexão fechada inesperadamente
                        f.write(chunk)
                        bytes_recebidos += len(chunk)
            else:
                print(f"[-] Erro do servidor: {resposta_inicial.decode().strip()}")
        except Exception as e:
            print(f"[-] Falha na comunicação: {e}")
        finally:
            client.close()


if __name__ == "__main__":
    cliente = ClientTCP(target_host, target_port)
    arquivo_desejado = "arquivo.txt"
    i = 0
    while i < 10:
        cliente.solicitar_arquivo(arquivo_desejado)
        i += 1


