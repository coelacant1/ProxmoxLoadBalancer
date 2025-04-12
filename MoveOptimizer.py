# Copyright (C) 2025 Coela Can't
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class MoveOptimizer:
    def __init__(self, moves):
        """
        Initialize the MoveOptimizer with a list of moves.

        :param moves: List of moves returned from the balancer.
        """
        self.moves = moves
        self.optimized_moves = {}

    def optimize(self):
        """
        Optimize the moves by combining intermediate moves into a single direct move.
        
        :return: List of optimized moves where each item moves from its initial position to its final position.
        """
        # Process each move from the balancer
        for move in self.moves:
            from_bucket = move['from']
            to_bucket = move['to']
            items = move['items']

            for item in items:
                item_id = item.id
                # If the item has already been moved, update its final destination
                if item_id in self.optimized_moves:
                    self.optimized_moves[item_id]['to'] = to_bucket
                else:
                    # If this is the first time we're seeing the item, store its initial move
                    self.optimized_moves[item_id] = {'from': from_bucket, 'to': to_bucket}

        # Convert the optimized move dictionary back to a list of moves
        result = []
        for item_id, move in self.optimized_moves.items():
            if move['from'] != move['to']:
                result.append({
                    'item_id': item_id,
                    'from': move['from'],
                    'to': move['to']
                })

        return result
