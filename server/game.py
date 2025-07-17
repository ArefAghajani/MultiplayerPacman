
import threading ,time , random

class Game:
    '''game kernel'''
    FPS = 30
    DELTA = 1 / FPS
    UNIT = 20
    HEIGHT = 30 * UNIT
    WIDTH = 56 * UNIT
    board = [
    "########################################################",
    "#............##............##............##............#",
    "#.####.#####.##.#####.####.##.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o##o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.##.####.#####.##.#####.####.#",
    "#..........................##..........................#",
    "#.####.##.########.##.####.##.####.##.########.##.####.#",
    "#.####.##.########.##.####.##.####.##.########.##.####.#",
    "#......##....##....##......##......##....##....##......#",
    "######.##### ## #####.############.##### ## #####.######",
    "######.##### ## #####.############.##### ## #####.######",
    "######.##          ##.############.##          ##.######",
    "######.## ###--### ##.############.## ###--### ##.######",
    "######.## #      # ##.############.## #      # ##.######",
    "###### ## #      # ##              ## #      # ## ######",
    "######.## #      # ##.############.## #      # ##.######",
    "######.## ######## ##.############.## ######## ##.######",
    "######.##          ##.############.##          ##.######",
    "######.## ######## ##.############.## ######## ##.######",
    "######.## ######## ##.############.## ######## ##.######",
    "#............##............##............##............#",
    "#.####.#####.##.#####.####.##.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.##.####.#####.##.#####.####.#",
    "#o..##................##..o##o..##................##..o#",
    "###.##.##.########.##.##.######.##.##.########.##.##.###",
    "###.##.##.########.##.##.######.##.##.########.##.##.###",
    "#......##....##....##......##......##....##....##......#",
    "#.##########.##.##########.##.##########.##.##########.#",
    "#.##########.##.##########.##.##########.##.##########.#",
    "#..........................##..........................#",
    "########################################################"
    ]
    SPEED = UNIT/5
    normal_R = UNIT / 6
    big_R = UNIT / 2.5
    ESCAPE_TIME = 10
    def __init__(self):
        self.stat = {0 : [] , 1 : [] , 2 : [] , 3 : [] , 4 : []} # 0 -> player 1 location and direction and mode , 1 --> player 2 , 2 --> small coins locations , 3 --> big coins locations , 4 --> ghosts locations
        self.player1 = [13 * self.UNIT, 17 * self.UNIT,1,0] # [x, y, direction, mode -> pacman(0) or ghost(1) ]
        self.player2 = [41 * self.UNIT, 17 * self.UNIT,3,0]
        self.coins = []
        self.big_coins = []
        self.ghosts = [[11 * self.UNIT , 11 * self.UNIT , 3 , 0 , True], [16 * self.UNIT, 11 * self.UNIT , 1 , 0 , True], [39 * self.UNIT, 11*self.UNIT , 1 , 0 , True], [44 * self.UNIT , 11 * self.UNIT , 3 , 0 , True]] # --> [x , y , direction , chase mode(0) or escape mode(1) , is moving]
        self.temp_dir_p1= 1
        self.temp_dir_p2 = 1
        self.p1_moving = [False]
        self.p2_moving = [False]
        self.p1_lose = [False]
        self.p2_lose = [False]
        self.walls = []
        self.ways = []
        self.crosses = {}
        self.p1_gain = [] # normal and big 
        self.p2_gain = [] # normal and big
        self.escape_timer = [0,0]
        self.vector = [(0,-1),(1,0),(0,1),(-1,0)]
        self.generate_board()
        self.coins_number =(len(self.coins) + len(self.big_coins)) /2
        # self.run()

    def run(self):

        if not (self.p1_lose[0] or self.p2_lose[0]):
            self.verify(self.player1 , self.temp_dir_p1)
            self.verify(self.player2 , self.temp_dir_p2)
            self.ghosts_move()
            self.ghost_collision()
            self.gain_all_coins()
            self.players_collison()
            self.move()
            self.coins_collision()
            self.big_coins_collision()
            #time.sleep(self.DELTA)

    def check_collision(self, player, moving):
        if (player[0] , player[1]) in self.ways:
            #print(player , moving)
            if ( player[0] +self.vector[player[2]][0] *self.UNIT , player[1] + self.vector[player[2]][1] * self.UNIT) in self.ways:
                if type(moving) == list:
                    moving[0] = True
                else:
                    moving = True
                #print(moving)
            else:
                if type(moving) == list:
                    moving[0] = False
                else:
                    moving = False
                #print(moving)
    def move(self):
        self.check_collision(self.player1, self.p1_moving)
        self.check_collision(self.player2, self.p2_moving)
        for (player , moving) in [(self.player1, self.p1_moving) , (self.player2 , self.p2_moving)]:
            if moving[0]:
                player[0] += self.vector[player[2]][0] * self.SPEED
                player[1] += self.vector[player[2]][1] * self.SPEED

    def verify(self, player , temp_dir):
        '''player : [x,y,dir,mode]
        player temp diection
        check that is it a possible move or not'''
        if (player[0], player[1]) in self.ways:
            if (player[0] + self.vector[temp_dir][0] * self.UNIT , player[1] + self.vector[temp_dir][1] * self.UNIT) in self.ways:
                player[-2] = temp_dir
        else:
            if (temp_dir + 2) % 4 == player[-2]:
                player[-2] = temp_dir

    def generate_board(self):
        for j , row in enumerate(self.board):
            for i , char in enumerate(row):
                if char == '.':
                    self.coins.append((i * self.UNIT , j * self.UNIT))
                if char == 'o':
                    self.big_coins.append((i * self.UNIT , j * self.UNIT))
                if char in ('#' , '-'):
                    self.walls.append((i * self.UNIT , j * self.UNIT))
                if char in (' ' , '.' , 'o'):
                    self.ways.append((i * self.UNIT , j * self.UNIT))
        for way in self.ways:
            # find the break and cross in ways
            x = []
            y = []
            for dir in range(4):
                point = (way[0] + self.vector[dir][0] * self.UNIT , way[1] + self.vector[dir][1] * self.UNIT)
                if point in self.ways:
                    if dir in (0 , 2) :
                        y.append(dir)
                    else:
                        x.append(dir)
            if x and y :
                self.crosses[way] = x + y

    def set_direction(self, p1direction:int = None , p2direction:int = None):
        '''directions : { 0 : up , 1 : right , 2 : down , 3 : left}'''
        #print([p1direction,p2direction])
        if p1direction is not None:
            self.temp_dir_p1 = p1direction
        if p2direction is not None:
            self.temp_dir_p2 = p2direction

    def ghosts_move(self):
        self.check_collision_ghosts()
        for ghost in self.ghosts:
            if not ghost[-1]:
                #print('hit')
                ghost[2] = random.choice(self.crosses[tuple(ghost[0:2])])
                ghost[-1] = True
                ghost[0] += self.vector[ghost[2]][0] * self.SPEED
                ghost[1] += self.vector[ghost[2]][1] * self.SPEED
            else:
                ghost[0] += self.vector[ghost[2]][0] * self.SPEED
                ghost[1] += self.vector[ghost[2]][1] * self.SPEED

    def check_collision_ghosts(self):
        for ghost in self.ghosts:
            if (ghost[0] , ghost[1]) in self.ways:
                #if ( ghost[0] +self.vector[ghost[2]][0] *self.UNIT , ghost[1] + self.vector[ghost[2]][1] * self.UNIT) in self.ways:
                if (ghost[0] , ghost[1]) in self.crosses:
                    #ghost[-1] = True
                    ghost[-1] = False
                else:         
                    #ghost[-1] = False
                    ghost[-1] = True
                    
    def coins_collision (self):
        for player, gain in ((self.player1 ,self.p1_gain), (self.player2 , self.p2_gain)):
            if not player[3] : 
                # ensure that is in pacman mode
                for coin in self.coins:
                    if player[0] - self.normal_R < coin[0] < player[0] + self.normal_R  and player[1] - self.normal_R< coin[1] < player[1] + self.normal_R :
                        gain.append(coin)
        for coin in (self.p1_gain + self.p2_gain):
            if coin in self.coins:
                self.coins.remove(coin)
    
    def big_coins_collision (self):
        for index , t in enumerate(self.escape_timer):
            if t and time.time() - t > self.ESCAPE_TIME:
                self.ghosts[2 *index][-2] = 0
                self.ghosts[2 *index + 1][-2] = 0
                self.escape_timer[index] = 0

                
        for index ,(player, gain, ghosts) in enumerate(((self.player1 ,self.p1_gain , self.ghosts[0:2]), (self.player2 , self.p2_gain , self.ghosts[2:4]))):
            if not player[-1] : 
                # ensure that is in pacman mode
                for coin in self.big_coins:
                    if player[0] - self.big_R < coin[0] < player[0] + self.big_R  and player[1] - self.big_R< coin[1] < player[1] + self.big_R :
                        for ghost in ghosts:
                            ghost[-2] = 1 # escape mode
                            self.escape_timer[index] = time.time()


                        gain.append(coin)
        for coin in (self.p1_gain + self.p2_gain):
            if coin in self.big_coins:
                self.big_coins.remove(coin)
    def stat_generator(self):
        self.stat[0] , self.stat[1] = self.player1 , self.player2
        self.stat[2]  = self.coins 
        self.stat[3] = self.big_coins
        self.stat[4] = self.ghosts
        return self.stat
    
    def ghost_collision(self):
        for index , ghost in enumerate(self.ghosts):
            if index in (0,1):
                if self.player1[0] - self.big_R<ghost[0]< self.player1[0] + self.big_R and self.player1[1] - self.big_R < ghost[1] < self.player1[1] + self.big_R:
                    if ghost[-2] == 0:
                        self.p1_lose[0]= True
                    else:
                        # return it to cage
                        ghost[0] , ghost[1] = 11*self.UNIT , 13 * self.UNIT

            else:
                if self.player2[0] - self.big_R<ghost[0]< self.player2[0] + self.big_R and self.player2[1] - self.big_R < ghost[1] < self.player2[1] + self.big_R:
                    if ghost[-2] == 0:
                        self.p2_lose[0] = True
                    else:
                        ghost[0] , ghost[1] =39*self.UNIT , 13 * self.UNIT
    def gain_all_coins(self):
        for player_gain , loser in( (self.p1_gain, self.p2_lose ), (self.p2_gain , self.p1_lose)):
            if len(player_gain) == self.coins_number:
                loser[0] = True
    def players_collison(self):

        for index , player in enumerate((self.player1 , self.player2)):
            if index == 0 :
                if player[0] >= 28 * self.UNIT :
                    player[3] = 1
                else: 
                    player[3] = 0
            else:
                if player[0] <= 28 * self.UNIT :
                    player[3] = 1
                else:
                    player[3] = 0
        if self.player1[0] - self.big_R < self.player2[0] < self.player1[0] + self.big_R and self.player1[1] - self.big_R < self.player2[1] < self.player1[1] + self.big_R :
            for index , t in enumerate(self.escape_timer):
                if t and time.time()-t < self.ESCAPE_TIME:
                    if index == 0 :
                        self.p2_lose[0] = True
                    if index == 1:
                        self.p1_lose[0] = True

            if self.player1[3] :
                self.p2_lose [0] = True
            if self.player2[3] :
                self.p1_lose[0] = True
