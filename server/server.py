import socket, threading, time, json, game
import game

class Server:
    FPS = 30
    UNIT = 20
    HEIGHT = 30 * UNIT
    WIDTH = 56 * UNIT

    def __init__(self, ip = '127.0.0.1', port = 9090):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip , port))
        print(f'server running on {ip}:{port}')
        self.pacman = game.Game()
        self.stat = self.pacman.stat_generator()
        #print(self.stat)

        while len(self.clients) < 2:
            data, client_address = self.server_socket.recvfrom(1024)
            print(f"Received {data.decode()} from {client_address}")
            if data.decode() == 'hello':
                self.clients.append(client_address)
            # wait for 2 players
        for index, value in enumerate(self.clients):
            self.server_socket.sendto(str(index).encode(),value)
            self.server_socket.sendto(f'you are player{index+1}'.encode(),value)
        for i in range(3, -1 ,-1):
                self.server_socket.sendto(str(i).encode(), self.clients[0])
                self.server_socket.sendto(str(i).encode(), self.clients[1])
                time.sleep(1)
        walls = json.dumps({ 'walls' :self.pacman.walls}).encode()
        self.server_socket.sendto(walls , self.clients[0])
        self.server_socket.sendto(walls , self.clients[1])

        self.broadcast_thr = threading.Thread(target=self.broadcaster)
        self.listener_thr = threading.Thread(target= self.listener)

        self.listener_thr.start()
        self.broadcast_thr.start()
    
    def broadcaster(self):
        while not (self.pacman.p1_lose[0] or self.pacman.p2_lose[0]):
            #calculate the frame
            self.pacman.run()
            self.stat = self.pacman.stat_generator()

            # send message
            msg = json.dumps(self.stat).encode()
            for client in self.clients:
                self.server_socket.sendto(msg, client)
            
            time.sleep(1/self.FPS)
        msg = json.dumps(['finish',f'winner : player{2 if self.pacman.p1_lose[0] else 1}']).encode()
        for client in self.clients:
            self.server_socket.sendto(msg , client)
        quit()

    def listener(self):
        while not (self.pacman.p1_lose[0] or self.pacman.p2_lose[0]):

            data, client = self.server_socket.recvfrom(1024)
            data = json.loads(data.decode())
            if 'finish' in data:
                print(data[1])
                break
            elif 'close' in data:
                if self.clients.index(client) == 0:
                    self.pacman.p1_lose[0] = True
                if self.clients.index(client) == 1:
                    self.pacman.p2_lose[0] = True
            else:
                player = self.clients.index(client)
                self.pacman.set_direction(p1direction= data['direction'] if player == 0 else None , p2direction= data['direction'] if player == 1 else None)


pacman_server = Server()