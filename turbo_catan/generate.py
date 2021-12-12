"""Generate Catan Board"""

import numpy as np
from turbo_catan.hexes import *
import random


class CatanBoard:
    def __init__(self, n_players, enable_bonus_rolls=True):

        self.n_players = n_players
        self._gen_config(enable_bonus_rolls)

    def gen_map(self):
        self.tiles = self._gen_tiles(self.n_players)

    def _gen_config(self, enable_bonus_rolls):

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
        self.roll_prob_lookup = {
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "8": 5,
            "9": 4,
            "10": 3,
            "11": 2,
        }

        # self.roll_select_prob -- for map generation, the weighted probability that the number will
        # be selected
        self.roll_select_prob = {
            "3": 1,
            "4": 1,
            "5": 1,
            "6": 1,
            "8": 1,
            "9": 1,
            "10": 1,
            "11": 1,
        }
        self.non_resource_tile_select_prob = {
            TileType.ocean: 0.75,
            TileType.desert: 0.25,
        }
        if enable_bonus_rolls == True:
            self.roll_prob_lookup.update({"2|12": 2, "2|2": 2, "12|12": 2})
            self.roll_select_prob.update({"2|12": 0.5, "2|2": 0.5, "12|12": 0.5})
        else:
            self.roll_prob_lookup.update({"2": 1, "12": 1})
            self.roll_select_prob.update({"2": 1, "12": 1})

        # tile placement config
        self.randomize_ring_placement = True

    def _gen_ring(self, ring):
        """Generates the coordinates of the specified ring number of tiles."""
        hex_coords = []
        for q in range(-ring, ring + 1):
            for r in range(-ring, ring + 1):
                s = -q - r
                Q = np.abs(q)
                R = np.abs(r)
                S = np.abs(s)
                if max(Q, R, S) == ring:
                    hex_coords.append((q, r, s))
        return hex_coords

    def _gen_coords(self, max_ring=2):
        """Generates coordinates for multiple rings, up to the specified max_ring and returns the list of tuples. Coordinate tuples are in Q,R,S format"""
        hex_coords = []
        for ring in range(max_ring + 1):
            ring_coords = self._gen_ring(ring)
            if self.randomize_ring_placement == True:
                random.shuffle(ring_coords)
            ring_coords.sort(key=lambda x: x[0] == 0 or x[1] == 0 or x[2] == 0)
            hex_coords += ring_coords
        return hex_coords

    def _gen_bag_of_rtiles(self, n_resource_tiles):
        """Create the bag of roll tiles to choose from"""
        bag_of_rtiles = []
        remainder_keys = []
        remainder_vals = []
        total_shares = sum(self.roll_select_prob.values())
        for key, value in self.roll_select_prob.items():

            expected_value = value * n_resource_tiles / total_shares
            bag_of_rtiles += [key] * int(expected_value)
            remainder_keys.append(key)
            remainder_vals.append(expected_value % 1)

        n_remaining_rtiles = n_resource_tiles - len(bag_of_rtiles)
        bag_of_rtiles += list(
            np.random.choice(
                remainder_keys,
                n_remaining_rtiles,
                p=np.array(remainder_vals) / sum(remainder_vals),
                replace=False,
            )
        )
        return bag_of_rtiles

    def _gen_rtiles(self, bag_of_rtiles, n_each_resource):
        # generate a set of rtiles for each resource type
        MAX_TRIES = 30
        i_loop = 0
        tiles = []
        while True:
            bag_of_rtiles_copy = bag_of_rtiles.copy()
            random.shuffle(bag_of_rtiles_copy)
            rtiles_per_res = []
            for i in range(len(RESOURCE_TILE_TYPES)):
                rtiles_per_res.append(
                    bag_of_rtiles_copy[i * n_each_resource : (i + 1) * n_each_resource]
                )

            # check to see if it is balanced
            total_pips = []
            for rtiles in rtiles_per_res:
                total_pips.append(sum([self.roll_prob_lookup[x] for x in rtiles]))
            total_pips = np.array(total_pips)

            x = np.mean(total_pips)

            if not np.any(
                (total_pips < self.roll_lower_bound_pct * x)
                | (total_pips > self.roll_upper_bound_pct * x)
            ):
                break

            i_loop += 1
            if i_loop > MAX_TRIES:
                raise Exception("couldnt generate rtiles")

        for i in range(len(RESOURCE_TILE_TYPES)):
            res = RESOURCE_TILE_TYPES[i]
            rolls = rtiles_per_res[i]
            for j in range(n_each_resource):
                tiles.append(Tile(res, rolls[j]))

        return tiles

    def _gen_tiles(self, n_players):
        """generates the tiles of a balanced map"""
        n_each_resource = int(
            np.ceil(n_players * self.resource_tiles_per_player)
            / len(RESOURCE_TILE_TYPES)
        )
        n_resource_tiles = int(n_each_resource) * len(RESOURCE_TILE_TYPES)
        n_non_resource = int(n_players * self.total_tiles_per_player - n_resource_tiles)

        bag_of_rtiles = self._gen_bag_of_rtiles(n_resource_tiles)

        tiles = []

        tiles += self._gen_rtiles(bag_of_rtiles, n_each_resource)

        non_resource_tile_types, non_resource_tile_probs = list(
            self.non_resource_tile_select_prob.keys()
        ), list(self.non_resource_tile_select_prob.values())
        for i in range(n_non_resource):
            res = np.random.choice(non_resource_tile_types, p=non_resource_tile_probs)
            tiles.append(Tile(res))

        random.shuffle(tiles)
        n_tiles = len(tiles)

        hex_coords = self._gen_coords(8)[:n_tiles]

        for i in range(n_tiles):
            tiles[i].set_coordinate(*hex_coords[i])

        self.tiles = tiles
        return tiles

    def plot(self):
        fig, ax = plot_hexes(self.tiles)
        ax.set_title(str(self.n_players) + " player map")
