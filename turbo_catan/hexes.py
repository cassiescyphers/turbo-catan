"""Generate Catan Board"""
from matplotlib import pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
import enum

class Tile:
    def __init__(self,type,num=None,r=None,q=None,s=None):
        self.type = type
        self.num = num
        
        if r != None and q != None and s != None:
            self.set_coordinate(r,q,s)
    def set_coordinate(self,r,q,s):
        self.r = r
        self.q = q
        self.s = s
        try:
            if r+q+s != 0:
                raise Exception("Invalid coordinate...")
        except:
            raise Exception("Invalid coordinate...")

class TileType(enum.Enum):
    wood = 1
    wheat = 2
    sheep = 3
    ore = 4
    brick = 5
    gold = 6
    desert = 7
    ocean = 8

    def to_color(self):
        ans = None
        if self == TileType.wood:
            ans = "green"
        elif self == TileType.wheat:
            ans = "yellow"
        elif self == TileType.brick:
            ans = "red"
        elif self == TileType.ocean:
            ans = "blue"
        elif self == TileType.desert:
            ans = "tan"
        elif self == TileType.ore:
            ans = "gray"
        elif self == TileType.sheep:
            ans = "lawngreen"
        elif self == TileType.gold:
            ans = "gold"

        else:
            raise Exception("I am overburdened.")

        return ans
ALL_TILE_TYPES = [TileType.wood,TileType.wheat,TileType.sheep,TileType.ore,TileType.brick,TileType.gold,TileType.desert,TileType.ocean]  

RESOURCE_TILE_TYPES = [TileType.brick,TileType.wood,TileType.sheep,TileType.wheat,TileType.ore]
NON_RESOURCE_TILE_TYPES = [TileType.ocean,TileType.desert]


    
def plot_hexes(tiles):
    '''
    tiles is a list of list representing rows and columns
    '''
    fig, ax = plt.subplots(1,figsize=(12,12))
    ax.set_aspect('equal')

    # Add some coloured hexagons
    hcoord = []
    vcoord = []
    for tile in tiles:
        x = tile.r
        y = 2. * np.sin(np.radians(60)) * (tile.q- tile.s) /3.
        hex = RegularPolygon((x, y), numVertices=6, radius=2. / 3., 
                             orientation=np.radians(30), 
                             facecolor=tile.type.to_color(), alpha=0.55, edgecolor='k')
        ax.add_patch(hex)
        # Also add a text label
        if tile.num:
            ax.text(x, y+0.2, str(tile.num), ha='center', va='center', size=18)

        vcoord.append(y)
        hcoord.append(x);

    # Also add scatter points in hexagon centres
    ax.scatter(hcoord, vcoord)

    return fig,ax