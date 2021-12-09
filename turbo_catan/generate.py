"""Generate Catan Board"""

import numpy as np
from hexes import *
import random
import math

class CatanBoard:
    def __init__(self,n_players,enable_bonus_rolls=True):
        
        self.n_players = n_players
        self._gen_config(enable_bonus_rolls)
        
    def gen_map(self):
        self.tiles = self._gen_tiles(self.n_players)
        

    def _gen_config(self,enable_bonus_rolls):
        
        # probability config
        self.roll_lower_bound_pct = 0.75
        self.roll_upper_bound_pct = 1.25
        
        # 3-4 players, 19 tiles
        # 5-6 players, 30 tiles
        # source: https://jkirschner.github.io/catan-randomizer/
        # shoot for 5.5 tiles per person
        self.resource_tiles_per_player = 5.5
        self.total_tiles_per_player = 7.0
        
        # probability config
        # self.roll_prob_lookup -- the probability (multiplied by 36) that the key number will 
        # roll in the game with 2 dice
        self.roll_prob_lookup = {"3":2,"4":3,"5":4,"6":5,"8":5,"9":4,"10":3,"11":2}
        
        # self.roll_select_prob -- for map generation, the weighted probability that the number will
        # be selected
        self.roll_select_prob = {"3":1,"4":1,"5":1,"6":1,"8":1,"9":1,"10":1,"11":1}
        self.non_resource_tile_select_prob = {TileType.ocean:0.75, TileType.desert:0.25}
        if enable_bonus_rolls == True:
            self.roll_prob_lookup.update({"2|12":2,"2|2":2,"12|12":2})
            self.roll_select_prob.update({"2|12":0.5,"2|2":0.5,"12|12":0.5})
        else:
            self.roll_prob_lookup.update({"2":1,"12":1})
            self.roll_select_prob.update({"2":1,"12":1})
            
            
        # tile placement config
        self.randomize_ring_placement = True
        self.prevent_single_edge_outer_ring_tiles = True
        
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
    def _calc_n_rings_needed(self,n_tiles):
        return math.ceil((-3 + math.sqrt(12*n_tiles - 3)) / 6) + 1
    
    def _gen_tile_templates(self,n_tiles):
        '''Generates a template board
        
            returns: template_hexes,outer_water_hexes
        '''            
        template_hexes = []
        
        n_rings_needed = self._calc_n_rings_needed(n_tiles)
        
        for i_ring in range(n_rings_needed):
            
            ring_coords = self._gen_ring(i_ring)
            
            if self.randomize_ring_placement == True:
                random.shuffle(ring_coords)
            if self.prevent_single_edge_outer_ring_tiles == True:
                ring_coords.sort(key=lambda x : x[0] == 0 or x[1] == 0 or x[2] == 0)
            
            
            
            
            if i_ring < (n_rings_needed - 1):
                allowed_tiles = ALL_TILE_TYPES
            else:
                ntake = n_tiles-len(template_hexes)
                
                outer_water_hexes = []
                for coord in ring_coords[ntake:]:
                    outer_water_hexes.append(Tile(TileType.ocean,None,*coord))

                ring_coords = ring_coords[:ntake]

                allowed_tiles = ALL_TILE_TYPES#RESOURCE_TILE_TYPES
            
            for ring_coord in ring_coords:
                template_hex = TileTemplate(*ring_coord,allowed_tiles)
                template_hexes.append(template_hex)
                
        
        return template_hexes,outer_water_hexes
    
    def _gen_bag_of_rtiles(self,n_resource_tiles):
        '''Create the bag of roll tiles to choose from'''
        bag_of_rtiles = []
        remainder_keys = []
        remainder_vals = []
        total_shares = sum(self.roll_select_prob.values())
        for key,value in self.roll_select_prob.items():

            expected_value = value*n_resource_tiles/total_shares
            bag_of_rtiles += [key] * int(expected_value)
            remainder_keys.append(key)
            remainder_vals.append(expected_value % 1)

        n_remaining_rtiles = n_resource_tiles - len(bag_of_rtiles)
        bag_of_rtiles += list(np.random.choice(remainder_keys,n_remaining_rtiles,p=np.array(remainder_vals)/sum(remainder_vals),replace=False))
        return bag_of_rtiles
    
    def _gen_rtiles(self,bag_of_rtiles,n_each_resource):
        # generate a set of rtiles for each resource type
        MAX_TRIES = 30
        i_loop = 0
        tiles = []
        while(True):
            bag_of_rtiles_copy = bag_of_rtiles.copy()
            random.shuffle(bag_of_rtiles_copy)
            rtiles_per_res = []
            for i in range(len(RESOURCE_TILE_TYPES)):
                rtiles_per_res.append(bag_of_rtiles_copy[i*n_each_resource:(i+1)*n_each_resource])

            # check to see if it is balanced
            total_pips = []
            for rtiles in rtiles_per_res:
                total_pips.append(sum([self.roll_prob_lookup[x] for x in rtiles]))
            total_pips = np.array(total_pips)

            x = np.mean(total_pips)

            if not np.any( (total_pips < self.roll_lower_bound_pct*x) | (total_pips > self.roll_upper_bound_pct*x) ):
                break
                
            i_loop += 1
            if i_loop > MAX_TRIES:
                raise Exception("couldnt generate rtiles")
        
        for i in range(len(RESOURCE_TILE_TYPES)):
            res = RESOURCE_TILE_TYPES[i]
            rolls = rtiles_per_res[i]
            for j in range(n_each_resource):
                    tiles.append(Tile(res,rolls[j]))
                
        return tiles
        
    
    def _gen_tiles(self,n_players):
        ''' generates the tiles of a balanced map'''
        n_each_resource =  int(np.ceil(n_players*self.resource_tiles_per_player) / len(RESOURCE_TILE_TYPES))
        n_resource_tiles = int(n_each_resource) * len(RESOURCE_TILE_TYPES)
        n_non_resource = int(n_players*self.total_tiles_per_player - n_resource_tiles)

        bag_of_rtiles = self._gen_bag_of_rtiles(n_resource_tiles)
        
        
        tiles = []
        
        tiles += self._gen_rtiles(bag_of_rtiles,n_each_resource)

        non_resource_tile_types,non_resource_tile_probs = list(self.non_resource_tile_select_prob.keys()), list(self.non_resource_tile_select_prob.values()) 
        for i in range(n_non_resource):
            res = np.random.choice(non_resource_tile_types,p=non_resource_tile_probs)
            tiles.append(Tile(res))
            
        n_tiles = len(tiles)

        template_hexes,outer_ocean_hexes = self._gen_tile_templates(n_tiles)
        
        # find the tiles that we need to place that have the least number of viable locations
        placement_results = []
        for tile_type in ALL_TILE_TYPES:
            viable_placements = [x for x in template_hexes if tile_type in x.allowed_types]
            n = len(viable_placements)
            
            placement_results.append((n,tile_type))

        placement_results.sort(key=lambda x : x[0])
           
        
        while(True): # attempt placement
            coordinate_assignments = {}
            n_placed = 0
            template_hexes_copy = template_hexes.copy()
            for n,tile_type in placement_results:
                
                viable_placements = [x for x in template_hexes_copy if tile_type in x.allowed_types]
                for tile in [x for x in tiles if x.type == tile_type]:
                    choice = np.random.choice(viable_placements)
                    coordinate_assignments[tile] = choice
                    viable_placements.remove(choice)
                    template_hexes_copy.remove(choice)
                    n_placed += 1

            if n_placed == n_tiles:
                break
            else:
                raise Exception("something broke." + str(n_placed ) + " " + str(n_tiles))
        
        
        for tile in tiles:
            c = coordinate_assignments[tile]
            tile.set_coordinate(c.q,c.r,c.s)
        tiles += outer_ocean_hexes

        self.tiles = tiles
        return tiles
    
    def plot(self):
        fig,ax = plot_hexes(self.tiles)
        ax.set_title(str(self.n_players) + " player map")
    
    
class TileTemplate:
    """Used to help assemble the map. Contains coordinates and probabilities that certain types of tiles will be placed here"""
    def __init__(self,q,r,s,allowed_types):
        self.q = q
        self.r = r
        self.s = s
        self.allowed_types = allowed_types
    
    def get_coordinates(self):
        return self.q,self.r,self.s
