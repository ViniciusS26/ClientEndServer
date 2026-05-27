import hashlib
import os  # Importado para manipulação de caminhos e verificação de arquivos
import socket
import threading

bind_ip = "95.58.0.3"
bind_port = 80

MATRICULA = "20219027928"
NOME = "VINICIUS DA SILVA NUNES"
# Definindo o diretório base onde os arquivos ficam salvos para segurança
DIRETORIO_ARQUIVOS = "./src/arquivos_servidor/"


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
        # Garante que a pasta de arquivos exista
        if not os.path.exists(DIRETORIO_ARQUIVOS):
            os.makedirs(DIRETORIO_ARQUIVOS)

        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.ip, self.port))
        self.servidor.listen(5)
        print(f"[*] Servidor TCP iniciado em {self.ip}:{self.port}")

    def handle_client(self, client_socket):
        try:
            # 1. Recebe a requisição inicial (Ex: "X-Custom-Auth: <hash>\nNomeDoArquivo.txt")
            mensagem_recebida = client_socket.recv(1024)
            print(f"[*] Requisição recebida raw: {mensagem_recebida}")

            # Separando as linhas (convenção comum: primeira linha o cabeçalho, segunda o arquivo solicitado)
            linhas = mensagem_recebida.split(b"\n")
            header_auth = linhas[0] if len(linhas) > 0 else b""
            nome_arquivo_bytes = (linhas[1].strip() if len(linhas) > 1 else b"")

            # 2. Validação do Cabeçalho de Autenticação
            if header_auth.startswith(b"X-Custom-Auth: "):
                hash_hex = header_auth[len(b"X-Custom-Auth: ") :].strip()
                hash_recebido = bytes.fromhex(hash_hex.decode())

                if hash_valida(hash_recebido):
                    print("[*] Hash válido. Processando pedido de arquivo...")

                    nome_arquivo = nome_arquivo_bytes.decode("utf-8")
                    # Evita Path Traversal (ex: o cliente pedir ../../arquivo.txt)
                    caminho_seguro = os.path.basename(nome_arquivo)
                    caminho_completo = os.path.join(DIRETORIO_ARQUIVOS, caminho_seguro)

                    # 3. Verificação e Envio do Arquivo
                    if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
                        # Envia um cabeçalho de sucesso informando o tamanho do arquivo
                        tamanho_arquivo = os.path.getsize(caminho_completo)
                        client_socket.send(f"OK|{tamanho_arquivo}\n".encode())

                        print(f"[*] Enviando {caminho_seguro} ({tamanho_arquivo} bytes)...")
                        # Abre o arquivo em modo binário e envia em blocos (chunks) de 4KB
                        with open(caminho_completo, "rb") as f:
                            while chunk := f.read(4096):
                                client_socket.sendall(chunk)
                        print("[*] Arquivo enviado com sucesso.")
                    else:
                        print(f"[-] Arquivo não encontrado: {caminho_seguro}")
                        client_socket.send(b"ERRO: Arquivo nao encontrado.\n")
                else:
                    print("[-] Hash inválido recebido.")
                    client_socket.send(b"ERRO: Hash invalido!\n")
            else:
                print("[-] Campo X-Custom-Auth ausente.")
                client_socket.send(b"ERRO: Campo X-Custom-Auth ausente.\n")

        except Exception as e:
            print(f"[-] Erro ao tratar cliente: {e}")
        finally:
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