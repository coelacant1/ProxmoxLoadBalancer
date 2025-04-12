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

class Bucket:
    def __init__(self, id, capacity, hostname=""):
        self.id = id
        self.capacity = capacity
        self.items = []
        self.hostname = hostname

    def add_item(self, item):
        """Add an item to the bucket."""
        if self.get_total_load() + item.load <= self.capacity:
            self.items.append(item)
        else:
            raise ValueError("Item exceeds bucket capacity.")

    def remove_item(self, item):
        """Remove an item from the bucket."""
        if item in self.items:
            self.items.remove(item)

    def get_total_load(self):
        """Calculate the total load in the bucket from its items."""
        return sum(item.load for item in self.items)

    def __repr__(self):
        return f"Bucket(id={self.id}, capacity={self.capacity}, total_load={self.get_total_load()}, items={len(self.items)})"
