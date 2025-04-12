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
from Bucket import Bucket
from Item import Item

class BucketSimulator:
    def __init__(self, bucket_capacity_list):
        self.buckets = [Bucket(i, cap) for i, cap in enumerate(bucket_capacity_list)]
        self.global_item_id = 0  # Global item ID counter to ensure uniqueness

    def generate_random_load_per_server(self):
        """Generates random load for each server (bucket) between 10% and 70% of capacity."""
        for bucket in self.buckets:
            # Generate a random load between 1% and 90% of the server's capacity
            load_percentage = random.uniform(0.01, 0.90)  # Random percentage between 10% and 70%
            target_load = int(bucket.capacity * load_percentage)

            # Fill the bucket with items until the target load is reached
            self.fill_bucket_with_items(bucket, target_load)

        return self.buckets

    def fill_bucket_with_items(self, bucket, target_load):
        """Fills a bucket with random block sizes that sum up to the target load."""
        block_sizes = [8, 8, 8, 8, 8, 8, 16, 16, 16, 16, 16, 16, 16, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 64, 128]  # Block sizes to use for filling
        
        remaining_load = target_load
        while remaining_load > 0:
            block = random.choice(block_sizes)
            if block > remaining_load:
                block = remaining_load  # Adjust block to exactly match remaining load
            
            # Create an item with a globally unique ID and add it to the bucket
            item = Item(self.global_item_id, bucket, block)
            bucket.add_item(item)

            # Increment the global item ID for the next item
            self.global_item_id += 1

            # Reduce the remaining load by the block size
            remaining_load -= block

    def simulate(self):
        """Run the simulation to generate random loads and fill servers with blocks."""
        self.generate_random_load_per_server()
        return self.buckets
