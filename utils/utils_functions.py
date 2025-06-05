from utils.Player import Player
from utils.Projectiles import Projectile

def broadcast_players_position(players_list:list[Player]):
    data = []
    for player in players_list:
        temp = {
            "name": player.name,
            "position": player.get_position()
        }
        data.append(temp)

    for player in players_list:
        player.get_stream().send_msg({
            "protocol": "positions",
            "data": data
        })
        
        
def broadcast_projectiles_position(projectiles_list:list[Projectile], players_list:list[Player]):
    data=[]
    for projectile in projectiles_list:
        temp={
            "name":projectile.get_player_name(),
            "position":projectile.get_position(),
            "vel":projectile.vel,
            "width":projectile.width,
            "height":projectile.heigth
        }
        data.append(temp)
    
    for player in players_list:
        player.get_stream().send_msg({
            "protocol": "projectiles",
            "data": data
        })