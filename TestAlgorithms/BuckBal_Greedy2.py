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

class BucketBalancer:
    def __init__(self, buckets):
        self.buckets = buckets
        self.tolerance = 0.05  # +/- 5% tolerance
        self.move_history = {}  # Track recent moves to avoid oscillation

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def target_load(self, bucket_capacity, total_capacity, total_load):
        """Calculate the target load for a bucket based on its capacity and total system load."""
        return (bucket_capacity / total_capacity) * total_load

    def is_within_tolerance(self, bucket_load, target_load):
        """Check if a bucket's load is within the +/- 5% tolerance."""
        return abs(bucket_load - target_load) <= target_load * self.tolerance

    def move_allowed(self, item, source, destination):
        """Check if a move is allowed to prevent back-and-forth oscillation."""
        last_move = self.move_history.get(item.id)
        return last_move != (destination.id, source.id)  # Ensure we don't undo the last move

    def record_move(self, item, source, destination):
        """Record a move in the move history to prevent immediate reversal."""
        self.move_history[item.id] = (source.id, destination.id)

    def balance_buckets(self):
        """Balance the load between buckets by moving the smallest item from the most overfilled bucket to the most underfilled bucket."""
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        total_load = self.get_total_load()  # Get the total system load once

        # Calculate the target load for each bucket
        targets = {bucket.id: self.target_load(bucket.capacity, total_capacity, total_load) for bucket in self.buckets}

        moves = []
        for _ in range(1000):  # Max iterations to avoid infinite loops
            # Cache the load for each bucket
            bucket_loads = {bucket.id: bucket.get_total_load() for bucket in self.buckets}

            # Find overfilled and underfilled buckets outside the +/- 5% tolerance
            overfilled = [bucket for bucket in self.buckets if not self.is_within_tolerance(bucket_loads[bucket.id], targets[bucket.id]) and bucket_loads[bucket.id] > targets[bucket.id]]
            underfilled = [bucket for bucket in self.buckets if not self.is_within_tolerance(bucket_loads[bucket.id], targets[bucket.id]) and bucket_loads[bucket.id] < targets[bucket.id]]

            if not overfilled or not underfilled:
                break  # No more buckets to balance

            # Sort overfilled by most overfilled and underfilled by most underfilled
            overfilled.sort(key=lambda b: bucket_loads[b.id] - targets[b.id], reverse=True)
            underfilled.sort(key=lambda b: targets[b.id] - bucket_loads[b.id])

            source = overfilled[0]  # The most overfilled bucket
            destination = underfilled[0]  # The most underfilled bucket

            # Move the smallest item from source to destination, only if allowed
            smallest_item = min(source.items, key=lambda item: item.load)
            if self.move_allowed(smallest_item, source, destination):
                # Simulate the move
                moves.append({'from': source.id, 'to': destination.id, 'items': [smallest_item]})

                # Remove item from source and add to destination
                source.remove_item(smallest_item)
                destination.add_item(smallest_item)

                # Record the move to prevent immediate reversal
                self.record_move(smallest_item, source, destination)

                # Update cached load values after the move
                bucket_loads[source.id] -= smallest_item.load
                bucket_loads[destination.id] += smallest_item.load

        return moves
