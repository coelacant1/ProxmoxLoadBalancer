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

import networkx as nx

class BucketBalancer:
    def __init__(self, buckets):
        self.buckets = buckets
        self.tolerance = 0.05  # +/- 5% tolerance

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def get_average_load(self):
        """Calculate the average load per bucket."""
        total_load = self.get_total_load()
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        return total_load / len(self.buckets)  # Average load per bucket

    def build_flow_network(self):
        """Build a flow network where nodes are buckets, and edges represent moves."""
        G = nx.DiGraph()

        average_load = self.get_average_load()

        source = "source"
        sink = "sink"
        G.add_node(source)
        G.add_node(sink)

        # Add nodes for each bucket and their connections
        for bucket in self.buckets:
            current_load = bucket.get_total_load()
            lower_bound = average_load * (1 - self.tolerance)
            upper_bound = average_load * (1 + self.tolerance)

            # If a bucket is underfilled, connect it to the source
            if current_load < lower_bound:
                G.add_edge(source, bucket.id, capacity=lower_bound - current_load, weight=0)

            # If a bucket is overfilled, connect it to the sink
            if current_load > upper_bound:
                G.add_edge(bucket.id, sink, capacity=current_load - upper_bound, weight=0)

            # Add edges between buckets to allow redistribution of items
            for other_bucket in self.buckets:
                if bucket != other_bucket:
                    G.add_edge(bucket.id, other_bucket.id, capacity=float('inf'), weight=1)  # Cost is 1 per move

        return G, source, sink

    def balance_buckets(self):
        """Solve the Min-Cost Max-Flow problem and move items between buckets accordingly."""
        G, source, sink = self.build_flow_network()

        try:
            flow_dict = nx.max_flow_min_cost(G, source, sink)
            cost = nx.cost_of_flow(G, flow_dict)

            print(f"Total cost (number of moves): {cost}")
            print("Flow distribution:")

            for u, flow in flow_dict.items():
                for v, f in flow.items():
                    if f > 0 and u != "source" and v != "sink":
                        print(f"Move {f} units from Bucket {u} to Bucket {v}")
                        self.move_items_between_buckets(u, v, f)

            return flow_dict
        except nx.NetworkXUnfeasible:
            print("No valid flow can satisfy all demands. Please check the capacities and loads.")
            return None

    def move_items_between_buckets(self, source_id, destination_id, amount_to_move):
        """Move items between two buckets based on the flow amount."""
        source_bucket = next(b for b in self.buckets if b.id == source_id)
        destination_bucket = next(b for b in self.buckets if b.id == destination_id)

        moved_amount = 0
        items_to_move = []

        # Select items from source to move to destination
        for item in source_bucket.items:
            if moved_amount + item.load <= amount_to_move:
                items_to_move.append(item)
                moved_amount += item.load

            if moved_amount >= amount_to_move:
                break

        # Perform the move: remove items from source and add to destination
        for item in items_to_move:
            source_bucket.remove_item(item)
            destination_bucket.add_item(item)

        print(f"Moved {moved_amount} units from Bucket {source_bucket.id} to Bucket {destination_bucket.id}")
