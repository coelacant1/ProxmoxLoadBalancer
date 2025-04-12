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
import colorsys  # For generating hues
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define a set of colors to assign to items based on their id
VISUALIZATION_WIDTH = 100  # Fixed width for all buckets' visualized blocks


class BucketVisualizer:
    def __init__(self, buckets, title):
        self.buckets = buckets
        self.title = title
        self.round_flip = False

    def scale_to_width(self, load, capacity):
        """Scales the load and capacity to fit within the fixed width."""
        load_ratio = load / capacity

        if self.round_flip:
            filled_units = int(math.ceil(load_ratio * VISUALIZATION_WIDTH))
            self.round_flip = False
        else:
            filled_units = int(math.floor(load_ratio * VISUALIZATION_WIDTH))
            self.round_flip = True

        return filled_units

    def hue_to_rgb(self, hue, brightness):
        """Converts a hue and brightness to an RGB color."""
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, brightness)
        return int(r * 255), int(g * 255), int(b * 255)

    def assign_colors(self):
        """Assigns a unique hue to each bucket and brightness to each item."""
        for bucket in self.buckets:
            hue = bucket.id / len(self.buckets)  # Unique hue for each bucket
            item_count = len(bucket.items)
            if item_count == 0:
                continue  # Skip buckets with no items
            
            for idx, item in enumerate(bucket.items):
                brightness = 0.5 + (idx / (2 * item_count))  # Brightness from 0.5 to 1.0
                
                if item.movable:
                    item.color = self.hue_to_rgb(hue, brightness)  # Assign RGB color to item
                else:
                    item.color = self.hue_to_rgb(hue, brightness - 0.25)  # Assign RGB color to item

    def rgb_to_ansi(self, r, g, b):
        """Converts an RGB value to an ANSI escape sequence for 24-bit color."""
        return f"\033[38;2;{r};{g};{b}m"

    def print_lines(self):
        print("=" * (VISUALIZATION_WIDTH + 50))  # Separator for the title

    def visualize(self):
        """Print-based visualization of bucket loads using custom colors."""
        print(f"\n{self.title}")
        self.print_lines()

        for bucket in self.buckets:
            total_capacity = bucket.capacity
            bucket_load = 0
            total_load = 0
            full_string = ""

            # Visualize load items in the bucket, using the item's color
            for item in bucket.items:
                item_size = self.scale_to_width(item.load, total_capacity)
                bucket_load += item.load
                total_load += item_size

                # Use the stored color for each item
                r, g, b = item.color
                color_ansi = self.rgb_to_ansi(r, g, b)
                
                full_string += color_ansi + '█' * item_size + Style.RESET_ALL  # Reset to default after color

            empty_part = ''
            if total_load != VISUALIZATION_WIDTH:
                empty_part = '░' * (VISUALIZATION_WIDTH - total_load)  # Empty space for unfilled capacity

            # Print bucket info with visualized load
            print(f"Bucket {bucket.id: <10} Host {bucket.hostname: <10} Load: {bucket_load:4.1f}\t / {bucket.capacity:4.1f}\t {bucket_load / bucket.capacity * 100.0:6.1f}%\t {full_string + empty_part}")

        self.print_lines()
