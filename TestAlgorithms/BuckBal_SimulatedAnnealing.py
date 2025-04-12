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

import random
import math

class BucketBalancer:
    def __init__(self, buckets, tolerance=0.05, initial_temp=1000, cooling_rate=0.99, min_temp=1):
        self.buckets = buckets
        self.tolerance = tolerance  # +/- 5% tolerance
        self.temperature = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def target_load(self, bucket_capacity, total_capacity, total_load):
        """Calculate the target load for a bucket based on its capacity and total system load."""
        return (bucket_capacity / total_capacity) * total_load

    def is_within_tolerance(self, bucket_load, target_load):
        """Check if a bucket's load is within the +/- 5% tolerance."""
        return abs(bucket_load - target_load) <= target_load * self.tolerance

    def get_balance_score(self, bucket_loads, targets):
        """Calculate a score based on how balanced the buckets are."""
        score = 0
        for bucket_id in bucket_loads:
            score += abs(bucket_loads[bucket_id] - targets[bucket_id])
        return score

    def cool_down(self):
        """Reduce the temperature according to the cooling rate."""
        self.temperature *= self.cooling_rate

    def accept_move(self, current_score, new_score):
        """Determine whether to accept a worse solution."""
        if new_score < current_score:
            return True
        else:
            # Accept worse solution with a probability based on temperature
            return random.random() < math.exp((current_score - new_score) / self.temperature)

    def balance_buckets(self):
        """Balance the load between buckets using simulated annealing."""
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        total_load = self.get_total_load()  # Get the total system load

        # Calculate the target load for each bucket
        targets = {bucket.id: self.target_load(bucket.capacity, total_capacity, total_load) for bucket in self.buckets}

        # Initial state
        bucket_loads = {bucket.id: bucket.get_total_load() for bucket in self.buckets}
        current_score = self.get_balance_score(bucket_loads, targets)

        moves = []
        while self.temperature > self.min_temp:
            # Generate a neighboring solution by randomly moving an item
            source = random.choice([b for b in self.buckets if b.items])  # Pick a random non-empty bucket
            destination = random.choice(self.buckets)  # Pick any bucket (could be the same)
            if source == destination:
                continue

            # Move a random item
            random_item = random.choice(source.items)

            # Check if destination bucket has enough capacity for the item
            if destination.get_total_load() + random_item.load <= destination.capacity:
                source.remove_item(random_item)
                destination.add_item(random_item)

                # Calculate the new bucket loads and the new balance score
                new_bucket_loads = {bucket.id: bucket.get_total_load() for bucket in self.buckets}
                new_score = self.get_balance_score(new_bucket_loads, targets)

                # Decide whether to accept the move
                if self.accept_move(current_score, new_score):
                    moves.append({'from': source.id, 'to': destination.id, 'items': [random_item]})
                    bucket_loads = new_bucket_loads
                    current_score = new_score
                else:
                    # Revert the move
                    destination.remove_item(random_item)
                    source.add_item(random_item)

                # Cool down the temperature
                self.cool_down()

        return moves
