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

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def target_load(self, bucket_capacity, total_capacity, total_load):
        """Calculate the target load for a bucket based on its capacity and total system load."""
        return (bucket_capacity / total_capacity) * total_load

    def balance_buckets(self):
        """Balance the load between buckets with optimization."""
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        total_load = self.get_total_load()  # Get the total system load once

        # Cache target load for each bucket
        targets = {bucket.id: self.target_load(bucket.capacity, total_capacity, total_load) for bucket in self.buckets}

        moves = []
        for _ in range(1000):  # Max iterations
            # Cache the load for each bucket to avoid recalculating repeatedly
            bucket_loads = {bucket.id: bucket.get_total_load() for bucket in self.buckets}

            # Find buckets that are overfilled or underfilled
            overfilled = sorted([bucket for bucket in self.buckets if bucket_loads[bucket.id] > targets[bucket.id]],
                                key=lambda b: bucket_loads[b.id] - targets[b.id], reverse=True)
            underfilled = sorted([bucket for bucket in self.buckets if bucket_loads[bucket.id] < targets[bucket.id]],
                                 key=lambda b: targets[b.id] - bucket_loads[b.id])

            if not overfilled or not underfilled:
                break  # No more buckets to balance

            for source in overfilled:
                for destination in underfilled:
                    # Calculate how much can be moved
                    move_amount = min(bucket_loads[source.id] - targets[source.id],
                                      targets[destination.id] - bucket_loads[destination.id])

                    items_to_move = []
                    current_move_size = 0

                    # Find items to move from source to destination
                    for item in source.items:
                        if current_move_size + item.load <= move_amount:
                            items_to_move.append(item)
                            current_move_size += item.load

                    # Only perform the move if we have items to move
                    if items_to_move:
                        # Simulate the move
                        moves.append({'from': source.id, 'to': destination.id, 'items': items_to_move})

                        # Remove items from the source and add them to the destination
                        for item in items_to_move:
                            source.remove_item(item)
                            destination.add_item(item)

                        # Update cached load values after the move
                        bucket_loads[source.id] -= current_move_size
                        bucket_loads[destination.id] += current_move_size

                    # Recalculate overfilled and underfilled buckets
                    overfilled = sorted([bucket for bucket in self.buckets if bucket_loads[bucket.id] > targets[bucket.id]],
                                        key=lambda b: bucket_loads[b.id] - targets[b.id], reverse=True)
                    underfilled = sorted([bucket for bucket in self.buckets if bucket_loads[bucket.id] < targets[bucket.id]],
                                         key=lambda b: targets[b.id] - bucket_loads[b.id])

                    if not overfilled or not underfilled:
                        break  # No more buckets to balance

        return moves
