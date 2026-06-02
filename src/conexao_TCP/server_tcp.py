import hashlib
import os  # Importado para manipulação de caminhos e verificação de arquivos
import socket
import threading

import time
import csv  # Importado para criação do arquivo CSV de logs



bind_ip = "95.58.0.3"
bind_port = 80

MATRICULA = "20219027928"
NOME = "VINICIUS DA SILVA NUNES"
# Definindo o diretório base onde os arquivos ficam salvos para segurança
DIRETORIO_ARQUIVOS = "./arquivos_servidor/"
LOG_FILE = "logs_transferencia.csv"

# Cria cabeçalho do CSV se o arquivo não existir
def gerar_cabecalho_csv():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Nome do Arquivo", "Tempo de Execução", "Taxa de Transferência"])





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

    def send_file(self, client_socket, caminho_arquivo):
        tamanho_arquivo = os.path.getsize(caminho_arquivo)
        total_byte_enviado = 0.0

        tempo_inicio = time.perf_counter()
        client_socket.send(f"OK|{tamanho_arquivo}\n".encode())
         # Abre o arquivo em modo binário e envia em blocos (chunks) de 4KB
        with open(caminho_arquivo, "rb") as f:
            while chunk := f.read(4096):
                client_socket.sendall(chunk)
                total_byte_enviado += len(chunk)

        tempo_fim = time.perf_counter()
        tempo_execucao = tempo_fim - tempo_inicio

        if tempo_execucao > 0:
            taxa_transferencia = total_byte_enviado / tempo_execucao
        
        return {
            "tempo_execucao": tempo_execucao, 
            "bytes_enviados": total_byte_enviado, 
            "taxa_transferencia":taxa_transferencia
        }             

    def cria_csv(self, nome_arquivo, tempo_execucao, taxa_transferencia):
        #criar linhas e colunas do csv
        with open(LOG_FILE, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([nome_arquivo, tempo_execucao, taxa_transferencia])


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
                    nome_arquivo = nome_arquivo_bytes.decode("utf-8")
                    # Evita Path Traversal (ex: o cliente pedir ../../arquivo.txt)
                    caminho_seguro = os.path.basename(nome_arquivo)
                    caminho_completo = os.path.join(DIRETORIO_ARQUIVOS, caminho_seguro)

                    # 3. Verificação e Envio do Arquivo
                    if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
                        # Envia um cabeçalho de sucesso informando o tamanho do arquivo
                        resultado = self.send_file(client_socket, caminho_completo)
                        
                        self.cria_csv(nome_arquivo, resultado['tempo_execucao'], resultado['taxa_transferencia'])
                        print(f"[*] Enviado '{nome_arquivo}' ({resultado['bytes_enviados']} bytes) em {resultado['tempo_execucao']:.2f} segundos (Taxa: {resultado['taxa_transferencia']:.2f} bytes/s)")
 
                    else:
                        client_socket.send(b"ERRO: Arquivo nao encontrado.\n")
                else:
                    client_socket.send(b"ERRO: Hash invalido!\n")
            else:
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
    gerar_cabecalho_csv()
    servidor.start_server()