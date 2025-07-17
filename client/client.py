import socket, pygame, json, threading, time

class Client:
    FPS = 30
    UNIT = 20
    HEIGHT = 31 * UNIT
    WIDTH = 56 * UNIT
    normal_R = UNIT / 6
    big_R = UNIT / 2.5

    def __init__(self, ip= '127.0.0.1' , port = 9090):
        self.runnig = [True]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.sendto('hello'.encode(), (ip, port))
        self.server_address = (ip, port)

        self.listen_thr = threading.Thread(target=self.listener)
        self.gui_thr = threading.Thread(target=self.gui)

        number , server = self.client_socket.recvfrom(4) 
        self.player_number = int(number.decode())
        data , server = self.client_socket.recvfrom(1024)
        print(data.decode())
        while True:
            data , server = self.client_socket.recvfrom(1024)
            data = data.decode()
            if data == '0':
                print('start')
                break
            print(data)

        self.walls , server = self.client_socket.recvfrom(1024 * 16)
        self.walls.decode()
        self.walls = json.loads(self.walls)['walls']
        self.listen_thr.start()
        self.gui_thr.start()

    def listener(self):
       self.stat = {}
       self.message = '' 
       while self.runnig[0]:
            data, server = self.client_socket.recvfrom(1024 * 8)
            data = json.loads(data.decode())
            if 'finish' in data:
                self.client_socket.sendto(json.dumps(data).encode() , server)
                print(data[1])
                self.message = data[1]
                self.runnig[0] = False
                
            else:
                for i in data:
                    self.stat[int(i)] = data[i]
    
    def gui(self):
        pygame.init()
        self.music_player()
        pygame.display.set_caption(f'player {self.player_number + 1}')
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.data = {'direction': 0}
        tag = True

        while self.runnig[0] :
            self.screen.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client_socket.sendto(json.dumps(['close']).encode(), self.server_address)
                    self.runnig[0] = False
                    tag = False
                    break
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.data = {'direction' : 0}
                        # print(self.data)
                        self.client_socket.sendto(json.dumps(self.data).encode(), self.server_address)
                    elif event.key == pygame.K_RIGHT:
                        self.data = {'direction' : 1}
                        # print(self.data)
                        self.client_socket.sendto(json.dumps(self.data).encode(), self.server_address)
                    elif event.key == pygame.K_DOWN:
                        self.data = {'direction' : 2}
                        # print(self.data)
                        self.client_socket.sendto(json.dumps(self.data).encode(), self.server_address)
                    elif event.key == pygame.K_LEFT:
                        self.data = {'direction' : 3}
                        # print(self.data)
                        self.client_socket.sendto(json.dumps(self.data).encode(), self.server_address)
            
            # rect = pygame.Rect(30,30,30,30)
            # pygame.draw.rect(self.screen , (255,255,255) , rect , 10)
            for wall in self.walls:
                wall_rect = pygame.Rect(wall[0] , wall[1] , self.UNIT , self.UNIT)
                pygame.draw.rect(self.screen ,(0,0,255), wall_rect)
            # noraml coin
            for coin in self.stat[2]:
                coin_rect = pygame.Rect(coin[0] , coin[1] , self.UNIT , self.UNIT)
                pygame.draw.circle(self.screen , (255,255,255) , coin_rect.center , self.normal_R)
            # big coin
            for big_coin in self.stat[3]:
                big_coin_rect = pygame.Rect(big_coin[0] , big_coin[1] , self.UNIT , self.UNIT)
                pygame.draw.circle(self.screen , (255,255,255) , big_coin_rect.center , self.big_R)

            #players
            for player in (self.stat[0] , self.stat[1]):
                #print(player)
                player_rect = pygame.Rect(player[0] , player[1] ,self.UNIT , self.UNIT)
                pygame.draw.circle(self.screen, (255, 255, 0) if not player[3] else (255, 192, 203) , player_rect.center , self.UNIT / 2 - 1)

            #ghosts
            for ghost in (self.stat[4]):
                pos = ghost[0:2]
                ghost_rect = pygame.Rect(pos[0] , pos[1] , self.UNIT , self.UNIT)
                pygame.draw.circle(self.screen,(255,0,0) if not ghost[3] else (173, 216, 230) , ghost_rect.center , self.UNIT /2 -1)

            pygame.display.update()
            self.clock.tick(self.FPS)
        if tag :
            font = pygame.font.Font('FreeSansBold.otf' , 52)
            self.text = font.render(self.message, True, (0,0,0),(255,255,255))
            self.text_rect = self.text.get_rect()
            self.text_rect.center = (self.WIDTH /2 , self.HEIGHT /2)
            self.screen.blit(self.text , self.text_rect)
            pygame.display.update()
            pygame.time.delay(5000)        
        pygame.quit()

    def music_player(self):
        pygame.mixer.init()
        pygame.mixer.music.load('music/music.mp3')
        pygame.mixer.music.play()
player = Client()