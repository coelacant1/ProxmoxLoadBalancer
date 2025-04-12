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

from ProxmoxManager import ProxmoxManager
from BucketBalancer import BucketBalancer
from BucketVisualizer import BucketVisualizer
from LoadStatistics import LoadStatistics
from MoveOptimizer import MoveOptimizer

# Proxmox API connection details
host = '192.168.1.10'
user = 'xxxxxx@pve'
password = 'ASecurePassword123'

# Initialize ProxmoxManager to manage Proxmox information
proxmox_manager = ProxmoxManager(host, user, password)

# Create buckets with initial loads
specific_hosts = ['pve01', 'pve02', 'pve03', 'pve04']
buckets_initial = proxmox_manager.get_buckets(host_names=specific_hosts)

# Visualize the initial state of the buckets
visualizer = BucketVisualizer(buckets_initial, "Initial Bucket Loads")
visualizer.assign_colors()
visualizer.visualize()
load_stats = LoadStatistics(buckets_initial)
std_dev_init = load_stats.calculate_standard_deviation()

# Balance the buckets based on the real node usage
balancer = BucketBalancer(buckets_initial)
moves = balancer.balance_buckets()

# Visualize the final state after balancing
visualizer = BucketVisualizer(buckets_initial, "Final Bucket Loads After Balancing")
visualizer.visualize()
load_stats = LoadStatistics(buckets_initial)
std_dev_post = load_stats.calculate_standard_deviation()

print(f"Initial Std Dev: {std_dev_init}, Post-Balancing Std Dev: {std_dev_post}")
print(f"Improvement: {(std_dev_init - std_dev_post) / std_dev_init * 100:.2f}%")

optimizer = MoveOptimizer(moves)
optimized_moves = optimizer.optimize()

# Print the final moves
for move in optimized_moves:
    print(f"Move item {move['item_id']} from Bucket {move['from']} to Bucket {move['to']}")
