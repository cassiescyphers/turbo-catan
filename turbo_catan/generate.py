"""Generate Catan Board"""

import numpy as np
from hexes import *
import random

class CatanBoard:
    def __init__(self,n_players,enable_bonus_rolls=True):
        
        self.n_players = n_players
        self._gen_config(enable_bonus_rolls)
        
    def gen_map(self):
        self.tiles = self._gen_tiles(self.n_players)
        

    def _gen_config(self,enable_bonus_rolls):
        self.target_avg_roll_probability = 3.0
        
        # 3-4 players, 19 tiles
        # 5-6 players, 30 tiles
        # source: https://jkirschner.github.io/catan-randomizer/
        # shoot for 5.5 tiles per person
        self.resource_tiles_per_player = 5.5
        self.total_tiles_per_player = 7.0
        
        # probability config
        self.roll_lower_bound_pct = 0.75
        self.roll_upper_bound_pct = 1.2
        # self.roll_prob_lookup -- the probability (multiplied by 36) that the key number will 
        # roll in the game with 2 dice
        self.roll_prob_lookup = {"3":2,"4":3,"5":4,"6":5,"8":5,"9":4,"10":3,"11":2}
        
        # self.roll_select_prob -- for map generation, the weighted probability that the number will
        # be selected
        self.roll_select_prob = {"3":1,"4":1,"5":1,"6":1,"8":1,"9":1,"10":1,"11":1}
        self.non_resource_tile_select_prob = {TileType.ocean:0.65, TileType.desert:0.35}
        if enable_bonus_rolls == True:
            self.roll_prob_lookup.update({"2|12":2,"2|2":2,"12|12":2})
            self.roll_select_prob.update({"2|12":0.5,"2|2":0.5,"12|12":0.5})
        else:
            self.roll_prob_lookup.update({"2":1,"12":1})
            self.roll_select_prob.update({"2":1,"12":1})
            
            
        # tile placement config
        self.randomize_ring_placement = True
        
    def _gen_ring(self,ring):
        '''Generates the coordinates of the specified ring number of tiles.'''
        hex_coords = []
        for q in range(-ring,ring+1):
            for r in range(-ring,ring+1):
                s = -q-r
                Q = np.abs(q)
                R = np.abs(r)
                S = np.abs(s)
                if max(Q,R,S) == ring:
                    hex_coords.append((q,r,s))
        return hex_coords
    def _gen_coords(self,max_ring = 2):
        '''Generates coordinates for multiple rings, up to the specified max_ring and returns the list of tuples. Coordinate tuples are in Q,R,S format'''
        hex_coords = []
        for ring in range(max_ring+1):
            ring_coords = self._gen_ring(ring)
            if self.randomize_ring_placement == True:
                random.shuffle(ring_coords)
            hex_coords += ring_coords
        return hex_coords

    def _gen_rolls(self,n,lower_bound_pct = .75, upper_bound_pct = 1.2):
        ''' Will generate n numbers (to place on hex tiles) that averages close to the configured target probability.'''
        roll_options,roll_options_probs = list(self.roll_select_prob.keys()),list(self.roll_select_prob.values())
        roll_options_probs /= np.sum(roll_options_probs)
        MAX_ROLLS = 1000
        i = 0
        while(True):
            i += 1
            rolls = np.random.choice(roll_options,n,p=roll_options_probs)
            mean_prob = np.mean([self.roll_prob_lookup[x] for x in rolls])
            if mean_prob < self.target_avg_roll_probability * upper_bound_pct and mean_prob > self.target_avg_roll_probability * lower_bound_pct:
                break
            if i == MAX_ROLLS:
                raise Exception("Couldn't generate rolls, try expanding the upper and lower bounds or changing the target probability.")
        return rolls
    
    def _gen_tiles(self,n_players):
        ''' generates the tiles of a balanced map'''
        n_each_resource =  int(np.ceil(n_players*self.resource_tiles_per_player) / len(RESOURCE_TILE_TYPES))
        n_resource_tiles = int(n_each_resource) * len(RESOURCE_TILE_TYPES)
        n_non_resource = int(n_players*self.total_tiles_per_player - n_resource_tiles)
        
        
        non_resource_tile_types,non_resource_tile_probs = list(self.non_resource_tile_select_prob.keys()), list(self.non_resource_tile_select_prob.values())
        tiles = []
        for res in RESOURCE_TILE_TYPES:
            rolls = self._gen_rolls(n_each_resource,self.roll_lower_bound_pct,self.roll_upper_bound_pct)
            for i in range(n_each_resource):
                tiles.append(Tile(res,rolls[i]))
        for i in range(n_non_resource):
            res = np.random.choice(non_resource_tile_types,p=non_resource_tile_probs)
            tiles.append(Tile(res))
            
        random.shuffle(tiles)
        n_tiles = len(tiles)
        
        hex_coords = self._gen_coords(8)[:n_tiles];
        
        for i in range(n_tiles):
            tiles[i].set_coordinate(*hex_coords[i])
        
        
            
        return tiles
    
    def plot(self):
        fig,ax = plot_hexes(self.tiles)
        ax.set_title(str(self.n_players) + " player map")
    
