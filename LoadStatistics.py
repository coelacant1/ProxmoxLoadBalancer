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

import math

class LoadStatistics:
    def __init__(self, buckets):
        self.buckets = buckets

    def calculate_mean_load(self):
        """Calculate the mean load across all buckets."""
        total_load = sum(bucket.get_total_load() for bucket in self.buckets)
        num_buckets = len(self.buckets)
        return total_load / num_buckets if num_buckets > 0 else 0

    def calculate_load_differences(self, mean):
        """Calculate the differences between each bucket's load and the mean load."""
        return [(bucket.get_total_load() - mean) for bucket in self.buckets]

    def calculate_variance(self, load_differences):
        """Calculate the variance of the load differences."""
        num_buckets = len(load_differences)
        if num_buckets == 0:
            return 0
        
        squared_diff_sum = sum(diff ** 2 for diff in load_differences)
        return squared_diff_sum / num_buckets

    def calculate_standard_deviation(self):
        """Calculate the standard deviation of the load differences between the buckets."""
        mean = self.calculate_mean_load()
        load_differences = self.calculate_load_differences(mean)
        variance = self.calculate_variance(load_differences)
        return math.sqrt(variance)

    def print_standard_deviation(self):
        """Print the standard deviation of the load differences between the buckets."""
        std_dev = self.calculate_standard_deviation()
        print(f"Standard Deviation of Load Differences Between Buckets: {std_dev:.2f}")
