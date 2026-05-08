# Segunda Avaliação de Redes de Computadores II 

## Objetivo

Implementar e comparar dois sistemas de transferência de arquivos: um utilizando o
protocolo TCP (nativo) e outro utilizando o protocolo UDP com uma camada de
confiabilidade (Reliable UDP) implementada pelo aluno. O foco é a validação cruzada
entre as métricas da aplicação e a inspeção do tráfego de rede.


### Objetivos Específicos

● Implementar controle de fluxo e de erros (Stop-and-Wait ou Go-Back-N) sobre
UDP.<br>
● Estruturar um protocolo de aplicação com cabeçalhos personalizados e
mecanismos de autenticação.<br>
● Simular condições adversas de rede (perda de pacotes e latência) no Docker.<br>
● Validar os dados estatísticos da aplicação com o Wireshark/TCPDump.<br>
○ Para isso, faça entre 10 e 30 execuções para gerar dados estatísticos:
vazão mínima, média, máxima e desvio padrão.<br>
● Gerar uma análise comparativa em Python (Pandas/Matplotlib) a partir de logs de
tráfego.

### Projeto

desenvolver um par Cliente/Servidor em Python capaz de operar em dois
modos:
1. Modo TCP: Transferência de arquivos por meio de sockets TCP padrão.<br>
2. Modo R-UDP (Reliable UDP): O aluno deve garantir a entrega íntegra do arquivo
sobre UDP, implementando:<br>
    ○ Números de sequência e confirmações (ACKs).<br>
    ○ Mecanismo de timeout e retransmissão.<br>

