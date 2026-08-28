
import socket
import random
import threading


CARTAS = [('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), 
           ('9', 9), ('10', 10), ('J', 10), ('Q', 10), ('A', 11)] * 4

class Deck:
    def __init__(self):
        self.cartas = CARTAS.copy()
        random.shuffle(self.cartas)
    
    def distribir(self):
        if not self.cartas:
            self.cartas = CARTAS.copy()
            random.shuffle(self.cartas)
        return self.cartas.pop()


class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((host, port))
        self.servidor.listen(5)
        print(f"Servidor em {host}:{port}")
    
    def ponto(self, cartas):
        p = sum(v for _, v in cartas)
        ases = sum(1 for _, v in cartas if v == 11)
        while p > 21 and ases:
            p -= 10
            ases -= 1
        return p
    
    def lidar(self, cliente, address):
        deck = Deck()
        jogador = [deck.distribir(), deck.distribir()]
        dealer = [deck.distribir(), deck.distribir()]
        
        while True:
            try:
                msg = f"\nSuas cartas: {[c[0] for c in jogador]}\nPonto: {self.ponto(jogador)}\nDealer: {[c[0] for c in dealer]}\nPonto: {self.ponto(dealer)}\n\nH(mais) ou S(parar)? "
                cliente.send(msg.encode())
                
                escolha = cliente.recv(1024).decode().upper()
                
                if escolha == 'H':
                    jogador.append(deck.distribir())
                    if self.ponto(jogador) > 21:
                        cliente.send("Você passou de 21! Perdeu.".encode())
                        break
                elif escolha == 'S':
                    while self.ponto(dealer) < 17:
                        dealer.append(deck.distribir())
                    
                    pj, pd = self.ponto(jogador), self.ponto(dealer)
                    if pj > pd:
                        cliente.send("Você venceu!".encode())
                    elif pj < pd:
                        cliente.send("Você perdeu!".encode())
                    else:
                        cliente.send("Empate!".encode())
                    break
            except:
                break
        
        cliente.close()
    
    def iniciar(self):
        while True:
            cliente, address = self.servidor.accept()
            threading.Thread(target=self.lidar, args=(cliente, address)).start()

# Cliente
class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = host, port
    
    def jogar(self):
        try:
            self.cliente.connect((self.host, self.port))
            print("Conectado!")
            
            while True:
                msg = self.cliente.recv(1024).decode()
                print(msg)
                
                if "venceu" in msg or "perdeu" in msg or "empate" in msg:
                    if input("Jogar novamente? (S/N): ").upper() != 'S':
                        break
                    self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.cliente.connect((self.host, self.port))
                else:
                    self.cliente.send(input("Sua escolha: ").upper().encode())
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            self.cliente.close()


if __name__ == "____main__":
    print("=== Blackjack (Socket) ===")
    print("1. Servidor\n2. Cliente")
    
    if input("Selecione: ") == '1':
        Server().iniciar()
    else:
        Client().jogar()

