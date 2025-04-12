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
        self.tolerance = 0.10  # +/- 5% tolerance

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def target_load(self, bucket_capacity, total_capacity, total_load):
        """Calculate the target load for a bucket based on its capacity and total system load."""
        return (bucket_capacity / total_capacity) * total_load

    def is_within_tolerance(self, bucket_load, target_load):
        """Check if a bucket's load is within the +/- 5% tolerance."""
        return abs(bucket_load - target_load) <= target_load * self.tolerance

    def balance_buckets(self):
        """Perform load balancing using First Fit Decreasing (Bin Packing) Algorithm."""
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        total_load = self.get_total_load()  # Get the total system load

        # Calculate target load for each bucket
        targets = {bucket.id: self.target_load(bucket.capacity, total_capacity, total_load) for bucket in self.buckets}

        # Extract all items from all buckets
        all_items = []
        for bucket in self.buckets:
            all_items.extend(bucket.items)

        # Sort items in decreasing order by their load
        all_items.sort(key=lambda item: item.load, reverse=True)

        # Clear buckets to reassign items using first-fit decreasing
        for bucket in self.buckets:
            bucket.items = []

        moves = []

        # Assign each item to the first bucket that can fit it within tolerance
        for item in all_items:
            for bucket in self.buckets:
                bucket_load = bucket.get_total_load()
                target_load = targets[bucket.id]

                # Check if adding this item will keep the bucket within +/- 5% tolerance
                if bucket_load + item.load <= target_load * (1 + self.tolerance):
                    bucket.add_item(item)
                    moves.append({'item': item.id, 'to_bucket': bucket.id})
                    break  # Move on to the next item once it's placed

        return moves

