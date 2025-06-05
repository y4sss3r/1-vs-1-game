import pygame
class Projectile:
    def __init__(self, x:int, y:int, width, heigth, vel, player_name):
        self.x=x
        self.y=y
        self.vel=vel
        self.width=width
        self.heigth=heigth
        self.player_name=player_name
        self.rect=pygame.Rect(self.x, self.y, self.width, self.heigth)
        self.color_setted=False
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_rect(self)->pygame.Rect:
        return self.rect

    def get_player_name(self):
        return self.player_name
    
    def update_position(self, new_x, new_y):
        self.x=new_x
        self.y=new_y
        return
    
    def set_color(self, color):
        self.color_setted=True
        self.color =color
    
    def get_color(self):
        if self.color_setted:
            return self.color
        else:
            raise Exception("color not setted")
    
    def move_rigth_screen(self):
        self.x+=self.vel
        self.rect.x=self.x
    
    def move_left_screen(self):
        self.x-=self.vel
        self.rect.x=self.x
    

class Projectile_manager:
    def __init__(self, screen_width, screen_heigth):
        self.projectiles=[]
        self.screen_width=screen_width
        self.screen_heigth=screen_heigth
        
    def shoot_projectile(self, projectile:Projectile, direction):
        if direction=="left" or direction=="right":
            temp={
                "projectile":projectile,
                "direction":direction
            }
            self.projectiles.append(temp)
        return
    
    
    def check_geometric_limtis(self, projectile: Projectile):
        if 0 <= projectile.x <= self.screen_width and 0 <= projectile.y <= self.screen_heigth:
            return
        self.projectiles = [
            p for p in self.projectiles if p["projectile"] != projectile
        ]
        
    def get_projectiles(self)->list[Projectile]:
        out:list[Projectile]=[]
        for proj_data in self.projectiles:
            projectile:Projectile=proj_data["projectile"]
            out.append(projectile)
        return out
    
    def update(self):
        for proj_data in self.projectiles:
            projectile:Projectile=proj_data["projectile"]
            direction=proj_data["direction"]
            if direction=="right":
                projectile.move_rigth_screen()
            elif direction=="left":
                projectile.move_left_screen()

            self.check_geometric_limtis(projectile)
    