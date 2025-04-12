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

from BucketBalancer import BucketBalancer
from BucketSimulator import BucketSimulator
from BucketVisualizer import BucketVisualizer
from LoadStatistics import LoadStatistics

# Example usage
bucket_capacity_list = [768, 656, 384, 384, 384, 384, 384, 384, 240, 240, 240, 240, 192]

# Initialize BucketSimulator to generate and distribute loads
simulator = BucketSimulator(bucket_capacity_list)
buckets_initial = simulator.simulate()

# Visualize initial state
visualizer = BucketVisualizer(buckets_initial, "Initial Bucket Loads")
visualizer.assign_colors()
visualizer.visualize()
load_stats = LoadStatistics(buckets_initial)
std_dev_init = load_stats.calculate_standard_deviation()

# Balance buckets
balancer = BucketBalancer(buckets_initial)
moves = balancer.balance_buckets()

# Visualize final state after balancing
visualizer = BucketVisualizer(buckets_initial, "Final Bucket Loads After Balancing")
visualizer.visualize()
load_stats = LoadStatistics(buckets_initial)
std_dev_post = load_stats.calculate_standard_deviation()

print(std_dev_init, std_dev_post, (std_dev_init - std_dev_post) / std_dev_init * 100)

# Print the final moves
for move in moves:
    items_moved = ', '.join(str(item) for item in move['items'])
    print(f"Move items [{items_moved}] from Bucket {move['from']} to Bucket {move['to']}")

