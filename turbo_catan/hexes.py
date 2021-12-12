"""Generate Catan Board"""
from matplotlib import pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
import enum
import math

class Tile:
    def __init__(self,type,num=None,q=None,r=None,s=None):
        self.type = type
        self.num = num
        self.r = None
        self.q = None
        self.s = None
        
        self.harbor = None
        self.harbor_position = 0
        
        if r != None and q != None and s != None:
            self.set_coordinate(q,r,s)
    def set_coordinate(self,q,r,s):
        self.r = r
        self.q = q
        self.s = s
        try:
            if r+q+s != 0:
                raise Exception("Invalid coordinate...")
        except:
            raise Exception("Invalid coordinate...")
    def get_coordinates(self):
        return self.q,self.r,self.s
    # helpers
    
    def get_adjacent_tiles(self,all_tiles):
        q,r,s = self.get_coordinates()
        at_c = [x.get_coordinates() for x in all_tiles]

        adj_t = {}

        adj_pos = [
            (q+1,r,s-1),
            (q,r+1,s-1),
            (q-1,r+1,s),
            (q-1,r,s+1),
            (q,r-1,s+1),
            (q+1,r-1,s),

        ]

        for i,p in enumerate(adj_pos):
            if p in at_c:
                adj_t[i] = all_tiles[at_c.index(p)]
        return adj_t
    
    
    
    # misc
    def __repr__(self):
        return str(self.type) + " tile @ " + str(self.get_coordinates())

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
            ans = "forestgreen"
        elif self == TileType.wheat:
            ans = "#F9F47A"
        elif self == TileType.brick:
            ans = "firebrick"
        elif self == TileType.ocean:
            ans = "dodgerblue"
        elif self == TileType.ore:
            ans = "silver"
        elif self == TileType.sheep:
            ans = "limegreen"
        elif self == TileType.desert:
            ans = "tan"
        elif self == TileType.gold:
            ans = "gold"

        else:
            raise Exception("I am overburdened: " + str(self))

        return ans
ALL_TILE_TYPES = [TileType.wood,TileType.wheat,TileType.sheep,TileType.ore,TileType.brick,TileType.gold,TileType.desert,TileType.ocean]  

RESOURCE_TILE_TYPES = [TileType.brick,TileType.wood,TileType.sheep,TileType.wheat,TileType.ore]
NON_RESOURCE_TILE_TYPES = [TileType.ocean,TileType.desert]

class Harbor(enum.Enum):
    wood = 1
    wheat = 2
    sheep = 3
    ore = 4
    brick = 5
    three_to_one = 6
    
    def to_color(self):
        ans = None
        if self == Harbor.wood:
            ans = "forestgreen"
        elif self == Harbor.wheat:
            ans = "#F9F47A"
        elif self == Harbor.brick:
            ans = "firebrick"
        elif self == Harbor.ore:
            ans = "silver"
        elif self == Harbor.sheep:
            ans = "limegreen"
        elif self == Harbor.three_to_one:
            ans = "whitesmoke"

        else:
            raise Exception("I am overburdened: " + str(self))

        return ans
    
def plot_hexes(tiles):
    '''
    tiles is a list of list representing rows and columns
    '''
    fig, ax = plt.subplots(1,figsize=(14,14))
    ax.set_aspect('equal')
    ax.set_facecolor('aliceblue')
    #ax.axis('off')
    #for side in ['top', 'bottom', 'left', 'right']:
    #    ax.spines[side].set_visible(False)
    
    ax.set_xticks([])
    ax.set_yticks([])

    # Add some coloured hexagons
    hcoord = []
    vcoord = []
    for tile in tiles:
        x = tile.r
        y = 2. * np.sin(np.radians(60)) * (tile.q- tile.s) /3.
        hex = RegularPolygon((x, y), numVertices=6, radius=2. / 3., 
                             orientation=np.radians(30), 
                             facecolor=tile.type.to_color(), alpha=1, edgecolor='k'
                            )
        ax.add_patch(hex)
        if tile.harbor != None:
            place_harbor(ax,x,y,tile.harbor,tile.harbor_position)
            
        # Also add a text label
        
        if tile.num:
            ax.text(x, y+0.2, str(tile.num), ha='center', va='center', size=18)

        vcoord.append(y)
        hcoord.append(x);

    # Also add scatter points in hexagon centres
    ax.scatter(hcoord, vcoord)

    return fig,ax

def place_harbor(ax,x,y,har,pos):
    ''' position is integer 0-5'''
    POLY_RADIUS = 2/3.
    
    a = np.deg2rad(-300-pos*60)
    pts = [(x,y),(x+POLY_RADIUS*math.cos(a),y+POLY_RADIUS*math.sin(a)),(x+POLY_RADIUS*math.cos(a+math.pi/3),y+POLY_RADIUS*math.sin(a+math.pi/3))]
    tri = plt.Polygon(pts,color=har.to_color())
    ax.add_patch(tri)
    
    return tri
    
    