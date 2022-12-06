import sys
import socket
import json
import threading


class Router:
    def __init__(self, name, ip, port, dist, next):
        self.enlace  = (name, ip, port)
        self.dist    = dist
        self.next    = next

    def get_enlace(self):
        return self.enlace

    def get_dist(self):
        return self.dist

    def get_next(self):
        return self.next

    def set_enlace(self, name, ip, port):
        self.enlace  = (name, ip, port)

    def set_dist(self, valor):
        self.dist = valor

    def set_next(self, next):
        self.next = next


mapa = []
flag = False
finish = False
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funções que lidam com cada ação entre roteadores
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def seguir_msg_adiante(text, origin, name, destin, next):
    msg = {
        "id": 9999,
        "name": name,
        "text": text,
        "origin": origin,
        "destin": destin,
        "next": next
    }
    for i in mapa:
        if i.get_enlace()[0] == next:
            h = i.get_enlace()[1]
            p = i.get_enlace()[2]
            try:
                s.sendto(json.dumps(msg).encode('utf-8'), 0, (h, int(p)))
                break
            except:
                i.set_dist(16)
                break

def enviar_atualizacao():
    nome = mapa[0].get_enlace()[0]
    msg = {
        "id": 11111,
        "name": nome
    }
    count = 0
    for i in mapa:
        msg[str(count)] = [i.get_enlace()[0], i.get_enlace()[1], i.get_enlace()[2], i.get_dist(), i.get_next()]
        count += 1
    msg["tam"] = len(mapa)
    for i in mapa:
        if i.get_dist() == 1:
            h = i.get_enlace()[1]
            p = int(i.get_enlace()[2])
            try:
                s.sendto(json.dumps(msg).encode('utf-8'), 0, (h,p))
            except:
                i.set_dist(16)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funções que lidam com cada comando da interface
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def conectar(ip, port, name):
    global flag
    flag = True
    mapa.append(Router(name,ip, port, 1, name)) 

def desconectar(ip, port):
    for i in mapa:
        if i.get_enlace()[1] == ip and i.get_enlace()[2] == port:
            i.set_dist(16)
            break

def rodar_alg():
    global flag
    flag = True
    while True:
        t = threading.Timer(1.0, enviar_atualizacao)
        t.start()

def finalizar():
    global finish
    finish = True
    sys.exit()

def print_tabela():
    print(str(mapa[0].get_enlace()[0]) + "\n")
    for i in mapa[1:]:
        print(str(i.get_enlace()[0]) + " " + str(i.get_dist()) + " " + str(i.get_next()) + "\n")
    print("\n")

def repassar_msg(text, destino):
    r_atual = mapa[0].get_enlace()[0]
    for i in mapa:
        if i.get_enlace()[0] == destino:
            # caso onde sabe-se a existencia de 'destin'
            print("E " + text + " de " + r_atual + " para " + destino + "\n")
            print("\n")
            seguir_msg_adiante(text, r_atual, r_atual, destino, i.get_next())
            return
    # caso onde não se sabe da existencia de 'destin'
    print("X " + text + " de " + r_atual + " para " + destino + "\n")
    print("\n") 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Função que lida com o recebimento de msgs
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
def receber_msgs_interface(msg):
    ident = msg["comando"]
    if   ident == "C":
        conectar(msg["param1"], msg["param2"], msg["param3"])
    elif ident == "D":
        desconectar(msg["param1"], msg["param2"])
    elif ident == "I":
        rodar_alg()
    elif ident == "F":
        finalizar()
    elif ident == "T":
        print_tabela()
    elif ident == "E":
        repassar_msg(msg["param1"], msg["param2"])

def receber_msgs_roteadores(msg, addr): 
    r_name  = msg["name"]
    r_atual = mapa[0].get_enlace()[0]
    isIn    = False
    for i in mapa:
        if i.get_enlace()[0] == r_name:
            isIn = True
            break
    if isIn == False:
        mapa.append(Router(r_name,addr[0], addr[1], 1, r_name))

    # msgs do protocolo de vetor de dist.
    if int(msg["id"]) == 11111:
        for num in range(int(msg["tam"])):
            isIn3 = False 
            for i in mapa:
                if msg[str(num)][0] == i.get_enlace()[0]: # se for o mesmo nome
                    if msg[str(num)][3]+1 < i.get_dist(): # se a dist nova for vantajosa
                        i.set_dist(msg[str(num)][3]+1)
                        i.set_next(r_name)
                    isIn3 = True
                    break
            if isIn3 == False:
                mapa.append(Router(msg[str(num)][0], msg[str(num)][1], msg[str(num)][2], msg[str(num)][3]+1, r_name)) 

    # msgs de encaminhamento de msgs
    elif int(msg["id"]) == 9999:
        # a msg é pra mim
        if msg["destin"] == r_atual:
            print("R " + msg["text"] + " de " + msg["origin"] + " para " + msg["destin"] + "\n")
            print("\n")
        else:
            isIn2 = False
            for i in mapa:
                # a msg n é pra mim mas conheço o alvo
                if i.get_enlace()[0] == msg["destin"]:
                    print("E " + msg["text"] + " de " + msg["origin"] + " para " +  msg["destin"] + " através de " + i.get_next() + "\n")
                    isIn2 = True
                    seguir_msg_adiante(msg["text"], msg["origin"], r_atual, msg["destin"], i.get_next())
                    break
            # a msg não é pra mim e não sei pra quem é
            if isIn2 == False:
                print("X " + msg["text"] + " de " + msg["origin"] + " para " +  msg["destin"] + "\n")
                print("\n")  

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Main e Loop de recebimento de novas conexões
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
HOST = sys.argv[1]
PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)

mapa.append(Router(HOST,IPAddr, PORT, 0, HOST)) 

s.bind((IPAddr, PORT))

try:
    while not(finish):
        msg, addr = s.recvfrom(1024)
        msg = json.loads(msg.decode('utf-8'))
        if int(msg["id"]) < 7:
            t0 = threading.Thread(target = receber_msgs_interface, args=[msg])
            t0.daemon = True
            t0.start()
        elif flag:
            t1 = threading.Thread(target = receber_msgs_roteadores, args=[msg, addr])
            t1.daemon = True
            t1.start()      
except:
    print("Error in main loop")   



    