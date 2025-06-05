
from utils.CommunicationProtocol import Protocol
from utils.Projectiles import Projectile
import pygame
class Player:
    def __init__(self, name, init_x:int, init_y:int, vel:int, color, width, heigth, hp=100):
        self.name=name
        self.x=int(init_x)
        self.y=int(init_y)
        self.hp=hp
        self.vel=int(vel)
        self.color=color
        self.stream_setted=False
        self.width=width
        self.heigth=heigth
        self.rect=pygame.Rect(self.x, self.y, self.width, self.heigth)
    
    def get_position(self):
        return self.x, self.y
    
    def get_rect(self)->pygame.Rect:
        return self.rect
    
    def get_color(self):
        return self.color
    
    def update_position(self, new_x:int, new_y:int):
        self.x=int(new_x)
        self.y=int(new_y)
        self.rect.topleft=(self.x, self.y)
        return
    
    def update_hp(self, new_hp):
        self.hp=new_hp
        return
    
    def move_up_screen(self):
        self.y-=self.vel
        
    def move_down_screen(self):
        self.y+=self.vel
    
    def move_rigth_screen(self):
        self.x+=self.vel
        
    def move_left_screen(self):
        self.x-=self.vel
    
    def set_stream(self, stream:Protocol):
        if not self.stream_setted:
            self.stream_setted=True
            self.stream=stream
    
    def get_stream(self) -> Protocol:
        if self.stream_setted:
            return self.stream
        else:
            raise Exception("stream is not setted for player obj")