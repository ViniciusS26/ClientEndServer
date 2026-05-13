import hashlib
import struct

# Dados do aluno para o Hash [cite: 30]
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