import socket
from utils.CommunicationProtocol import Protocol
from utils.Player import Player
from utils.Projectiles import Projectile, Projectile_manager
from utils.utils_functions import *
import threading
import pygame
import time, math

class GameServer:
    def __init__(self, player_name_1: str, conn_1: socket.socket, player_name_2: str, conn_2: socket.socket):
        # CONNECTIONS
        self.A_stream = Protocol(conn_1)
        self.B_stream = Protocol(conn_2)
        self.streams: list[Protocol] = [self.A_stream, self.B_stream]

        # GAME SETTINGS
        self.width_screen = 800
        self.heigth_screen = 800
        self.colors = {
            "bianco": (255, 255, 255),
            "rosso": (255, 0, 0),
            "nero": (0, 0, 0),
            "acqua": (0, 255, 255),
            "pink": (255, 0, 255)
        }
        
        self.player_vel=5
        self.player_width=30
        self.player_heigth=30
        
        self.proj_vel=15
        self.proj_width=15
        self.proj_heigth=45
        
        self.proj_manager=Projectile_manager(self.width_screen, self.heigth_screen)
        
        
        # PLAYER OBJECTS
        self.playerA=Player(player_name_1, self.width_screen // 8, self.heigth_screen // 2, self.player_vel, self.colors["acqua"], self.player_width, self.player_heigth)
        self.playerA.set_stream(self.A_stream)
        self.playerB=Player(player_name_2, 7*self.width_screen // 8, self.heigth_screen // 2, self.player_vel, self.colors["pink"], self.player_width, self.player_heigth)
        self.playerB.set_stream(self.B_stream)
        self.players:list[Player]=[self.playerA, self.playerB]
        

    def send_data(self, obj_protocol: Protocol, protocol: str, data):
        obj_protocol.send_msg({
            "protocol": protocol,
            "data": data
        })

    def start(self):
        print("game started")
        self.send_data(self.A_stream, "game", "started")
        self.send_data(self.B_stream, "game", "started")

        ready_streams = []
        for stream in self.streams:
            packet = stream.recv_msg()
            if packet["protocol"] == "game" and packet["data"] == "ready":
                print("Giocatore pronto")
                ready_streams.append(stream)

        print("Sending pygame info...")

        for stream in self.streams:
            stream.send_msg({
                "protocol": "window_dimensions",
                "data": {
                    "screen_heigth": self.heigth_screen,
                    "screen_width": self.width_screen
                }
            })
            stream.send_msg({
                "protocol": "player_dimensions",
                "data": {
                    "width": self.player_width,
                    "heigth": self.player_heigth,
                    "velocity": self.player_vel
                }
            })

        self.send_data(self.A_stream, "init_positions", {
            "self": (self.playerA.x, self.playerA.y),
            "enemy": (self.playerB.x, self.playerB.y),
            "angle_rotation": -math.pi/2
        })
        self.send_data(self.B_stream, "init_positions", {
            "self": (self.playerB.x, self.playerB.y),
            "enemy": (self.playerA.x, self.playerA.y) ,
            "angle_rotation": math.pi/2
        })

        self.send_data(self.A_stream, "color", self.playerA.color)
        self.send_data(self.B_stream, "color", self.playerB.color)

        time.sleep(0.5)
        for stream in self.streams:
            threading.Thread(target=self.wait_for_packets, args=(stream, ), daemon=True).start()
            self.send_data(stream, "plot", "start")
        time.sleep(0.5)
        threading.Thread(target=self.broadcast_info, daemon=True).start()
        
            
            
    def broadcast_info(self):
        while True:
            time.sleep(1/60)
            broadcast_players_position(self.players)
            broadcast_projectiles_position(self.proj_manager.get_projectiles(), self.players)
            self.proj_manager.update()
            
            

    def wait_for_packets(self, stream:Protocol):
        while True:
            packet=stream.recv_msg()
            print(packet)
            protocol=packet["protocol"]
            data=packet["data"]
            match protocol:
                case "rfm":
                    invert=True if int(data["angle_rotation"])<0 else False
                    player=self.get_player_by_name(data["name"])
                    match data["rel_direction"]: # 
                        case "up":
                            player.move_rigth_screen() if invert else player.move_left_screen()
                        case "down":
                            player.move_rigth_screen() if not invert else player.move_left_screen()
                        case "left":
                            player.move_up_screen() if invert else player.move_down_screen()
                        case "rigth":
                            player.move_up_screen() if not invert else player.move_down_screen()
                
                case "rff":
                    invert=True if int(data["angle_rotation"])<0 else False
                    player=self.get_player_by_name(data["name"])
                    projectile=Projectile(player.x, player.y, self.proj_width, self.proj_heigth, self.proj_vel, player.name)
                    direction="left" if not invert else "right"
                    self.proj_manager.shoot_projectile(projectile, direction)
                    
    
    def get_player_by_name(self, name) -> Player:
        for player in self.players:
            if player.name==name:
                return player
            

class GameClient:
    def __init__(self, server_conn: socket.socket, my_name, enemy_name):
        self.server_stream = Protocol(server_conn)
        self.my_name=my_name
        self.enemy_name=enemy_name
        self.colors = {
            "bianco": (255, 255, 255),
            "nero": (0, 0, 0),
            "rosso":(255, 0, 0),
            "acqua": (0, 255, 255),
            "pink": (255, 0, 255)
        }
        self.FPS = 60
        self.ready = threading.Event()
        
        self.my_bullets:list[Projectile]=[]
        self.enemy_bullets:list[Projectile]=[]
        self.bullet_damage=40
        
        self.can_shoot=True
        self.can_dmg_me=True
        self.can_dmg_enemy=True

    def send_data(self, protocol: str, data):
        self.server_stream.send_msg({
            "protocol": protocol,
            "data": data
        })

    def plot_game(self):
        pygame.init()
        win = pygame.display.set_mode((self.width, self.heigth))
        pygame.display.set_caption("1 vs 1")
        clock = pygame.time.Clock()
        
        self.my_player=Player(self.my_name, self.my_x, self.my_y, self.vel, self.my_color, self.player_width, self.player_heigth)
        self.enemy_player=Player(self.enemy_name, self.enemy_x, self.enemy_y, self.vel, self.enemy_color, self.player_width, self.player_heigth)
        self.players:list[Player]=[self.my_player, self.enemy_player]
        
        running = True
        while running:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            win.fill(self.colors["nero"])
            
            for player in self.players:
                player.x, player.y=player.get_position()
                #print(player.x, player.y)
                pygame.draw.rect(win, player.color, (player.x, player.y, self.player_width, self.player_heigth))
                
            for bullet in self.my_bullets:
                bullet_rect:pygame.Rect=bullet.get_rect()
                x, y=bullet.get_position()
                bullet_rect.topleft=(x, y)
                pygame.draw.rect(win, bullet.color, bullet_rect)
                if bullet.get_rect().colliderect(self.enemy_player.get_rect()) and self.can_dmg_enemy:
                    self.enemy_player.hp-=self.bullet_damage
                    self.can_dmg_enemy=False
                if not bullet.get_rect().colliderect(self.enemy_player.get_rect()):
                    self.can_dmg_enemy=True
            
            for bullet in self.enemy_bullets:
                bullet_rect:pygame.Rect=bullet.get_rect()
                x, y=bullet.get_position()
                bullet_rect.topleft=(x, y)
                pygame.draw.rect(win, bullet.color, bullet_rect)
                if bullet.get_rect().colliderect(self.my_player.get_rect()) and self.can_dmg_me:
                    self.my_player.hp-=self.bullet_damage
                    self.can_dmg_me=False
                if not bullet.get_rect().colliderect(self.my_player.get_rect()):
                    self.can_dmg_me=True
                
            if self.my_player.hp>0:
                self.controls()
                
            print(f"you: {self.my_player.hp}")
            print(f"enemy: {self.enemy_player.hp}")
            
            pygame.display.flip()

        pygame.quit()
    
    def controls(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.send_data("rfm", {"angle_rotation":self.angle_rotation, "rel_direction":"left", "name":self.my_name})
        if keys[pygame.K_RIGHT]:
            self.send_data("rfm", {"angle_rotation":self.angle_rotation, "rel_direction":"rigth", "name":self.my_name})
        if keys[pygame.K_UP]:
            print("pressed")
            self.send_data("rfm", {"angle_rotation":self.angle_rotation, "rel_direction":"up", "name":self.my_name})
        if keys[pygame.K_DOWN]:
            self.send_data("rfm", {"angle_rotation":self.angle_rotation, "rel_direction":"down", "name":self.my_name})
            
        if keys[pygame.K_SPACE] and self.can_shoot:
            self.can_shoot=False
            self.send_data("rff", {"angle_rotation":self.angle_rotation, "name":self.my_name})
        
        if not keys[pygame.K_SPACE]:
            self.can_shoot=True

    def wait_for_packets(self):
        while True:
            packet = self.server_stream.recv_msg()
            #print(packet)
            protocol = packet["protocol"]

            if protocol == "window_dimensions":
                self.heigth = packet["data"]["screen_heigth"]
                self.width = packet["data"]["screen_width"]
                self.center_rotation_x, self.center_rotation_y=self.width//2, self.heigth//2

            elif protocol == "init_positions":
                #print(packet["data"])
                x, y = packet["data"]["self"]
                ex, ey = packet["data"]["enemy"]
                self.angle_rotation=packet["data"]["angle_rotation"]
                #print(self.angle_rotation)
                self.my_x, self.my_y=self.apply_rotation(x, y, self.center_rotation_x, self.center_rotation_y, self.angle_rotation)
                self.enemy_x, self.enemy_y =self.apply_rotation(ex, ey, self.center_rotation_x, self.center_rotation_y, self.angle_rotation)

            elif protocol == "color":
                self.my_color = tuple(packet["data"])
                r, g, b= self.my_color  
                if r==255 and g==0 and b==255:
                    self.enemy_color = (0, 255, 255) 
                else: 
                    self.enemy_color = (255, 0, 255) 

            elif protocol == "player_dimensions":
                self.player_width = packet["data"]["width"]
                self.player_heigth = packet["data"]["heigth"]
                self.vel=packet["data"]["velocity"]

            elif protocol == "plot":
                self.ready.set()
                threading.Thread(target=self.plot_game, daemon=True).start()
                
            elif protocol== "positions":
                #print(packet["data"])
                for data in packet["data"]:
                    for player in self.players:
                        if player.name==data["name"]:
                            x=int(data["position"][0])
                            y=int(data["position"][1])
                            x, y= self.apply_rotation(x, y, self.width//2, self.heigth//2, self.angle_rotation)
                            player.update_position(x, y)
            
            elif protocol=="projectiles":
                self.my_bullets=[]
                self.enemy_bullets=[]
                for data in packet["data"]:
                    x, y = data["position"]
                    vel=data["vel"]
                    width=data["width"]
                    height=data["height"]
                    xp, yp = self.apply_rotation(x, y, self.center_rotation_x, self.center_rotation_y, self.angle_rotation)
                    bullet=Projectile(xp, yp, width, height, vel, data["name"])
                    if data["name"]==self.my_name:
                        color=self.colors["bianco"]
                        bullet.set_color(color)
                        self.my_bullets.append(bullet)
                    else:
                        color=self.colors["rosso"]
                        bullet.set_color(color)
                        self.enemy_bullets.append(bullet)
                    


    def start(self):
        threading.Thread(target=self.wait_for_packets, daemon=False).start()
        self.send_data("game", "ready")
        self.ready.wait()

    def apply_rotation(self, x:int, y:int, center_x, center_y, angle):# angle in rads
        x_rot=math.cos(angle)*(x - center_x) - math.sin(angle)*(y - center_y) + center_x
        y_rot=math.sin(angle)*(x - center_x) + math.cos(angle)*(y - center_y) + center_y
        
        return (x_rot, y_rot)