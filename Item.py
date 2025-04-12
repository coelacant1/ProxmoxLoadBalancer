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

class Item:
    def __init__(self, id, bucket, load, movable=True, color=None):
        """
        Initialize an item in the bucket.

        :param id: Unique identifier for the item.
        :param bucket: The bucket to which this item belongs.
        :param load: The load (memory usage) of the item.
        :param movable: Whether the item can be moved (True for dynamic, False for static).
        """
        self.id = id
        self.bucket = bucket
        self.load = load
        self.movable = movable  # True if the item can be moved, False otherwise
        self.color = color

    def __repr__(self):
        return f"Item(id={self.id}, load={self.load}, movable={self.movable})"