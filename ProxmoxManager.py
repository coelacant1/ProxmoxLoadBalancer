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

from proxmoxer import ProxmoxAPI
from Bucket import Bucket
from Item import Item

class ProxmoxManager:
    def __init__(self, host, user, password, verify_ssl=False):
        self.proxmox = ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)

    def get_node_usage(self):
        """Retrieve memory and CPU usage for each node in GB."""
        nodes = self.proxmox.nodes.get()
        node_stats = {}
        for node in nodes:
            node_name = node['node']
            status = self.proxmox.nodes(node_name).status.get()
            if 'memory' in status:
                memory_info = status['memory']
                memory_total_gb = memory_info['total'] / 1073741824  # Convert from bytes to GB
                memory_used_gb = memory_info['used'] / 1073741824  # Convert from bytes to GB
                memory_used_percentage = memory_used_gb / memory_total_gb * 100  # percentage
                node_stats[node_name] = {
                    'cpu': status['cpu'],
                    'memory_used': memory_used_gb,
                    'memory_used_percentage': memory_used_percentage,
                    'max_memory': memory_total_gb,
                    'memory_free': memory_total_gb - memory_used_gb,
                    'cpu_info': status.get('cpuinfo', {})
                }
            else:
                print(f"Memory information not available for node {node_name}")
                node_stats[node_name] = {
                    'cpu': status.get('cpu', 0),
                    'memory_used': 0,
                    'memory_used_percentage': 0,
                    'max_memory': 0,
                    'memory_free': 0,
                    'cpu_info': status.get('cpuinfo', {})
                }
        return node_stats

    def group_nodes_by_cpu(self, node_stats):
        """Group nodes by their CPU model and core count."""
        groups = {}
        for node, stats in node_stats.items():
            cpu_key = (stats['cpu_info'].get('model', ''), stats['cpu_info'].get('cpus', 0))  # Define group by CPU model and quantity
            if cpu_key not in groups:
                groups[cpu_key] = []
            groups[cpu_key].append(node)
        return groups

    def calculate_group_avg(self, group, node_stats):
        """Calculate average memory usage for a group of nodes."""
        total_memory = 0
        total_nodes = len(group)
        for node in group:
            total_memory += node_stats[node]['memory_used_percentage']
        return total_memory / total_nodes if total_nodes > 0 else 0

    def get_vm_stats(self, node):
        """Get a list of VMs on the node with their memory usage."""
        vms = self.proxmox.nodes(node).qemu.get()
        vm_stats = []
        for vm in vms:
            vmid = vm['vmid']
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            if 'mem' in vm_status:
                vm_stats.append({
                    'vmid': vmid,
                    'memory_used': vm_status['mem'] / 1073741824
                })
        return sorted(vm_stats, key=lambda vm: vm['memory_used'], reverse=True)

    def get_powered_on_vms(self, node):
        """Retrieve a list of powered-on VMs on the node with their memory usage."""
        powered_on_vms = []
        
        # Get all VMs on the node
        try:
            vms = self.proxmox.nodes(node).qemu.get()
        except Exception as e:
            print(f"Failed to retrieve VMs for node {node}: {e}")
            return powered_on_vms  # Return empty list if there's an error
        
        # Iterate through the VMs and check their status
        for vm in vms:
            vmid = vm['vmid']
            
            # Get current status of the VM
            try:
                vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
                
                # Only consider powered-on (running) VMs
                if vm_status['status'] == 'running':
                    memory_used_gb = vm_status['mem'] / 1073741824  # Convert from bytes to GB
                    
                    powered_on_vms.append({
                        'vmid': vmid,
                        'memory_used': memory_used_gb  # Memory usage in GB
                    })
            except Exception as e:
                print(f"Failed to retrieve status for VM {vmid} on node {node}: {e}")
        
        # Return the list of powered-on VMs
        return powered_on_vms

    def calculate_balance_percentage(self, group, node_stats, avg_memory):
        """Calculate how close the group is to being balanced in terms of memory utilization."""
        total_difference = 0
        for node in group:
            total_difference += abs(node_stats[node]['memory_used'] - avg_memory)
        
        # If total difference is 0, it's perfectly balanced
        total_nodes = len(group)
        return 100 - (total_difference / total_nodes)  # Higher percentage means closer to balance

    def output_nodes_vms_memory(self, node_stats):
        """Print node names with each VM's memory usage as a ratio of allocated memory."""
        
        def get_powered_on_vms(node):
            """Retrieve a list of powered-on VMs and their memory usage for a given node."""
            powered_on_vms = []
            vm_stats = self.get_vm_stats(node)
            for vm in vm_stats:
                vmid = vm['vmid']
                try:
                    vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
                    if vm_status['status'] == 'running':  # Only consider VMs that are online
                        mem = vm['memory_used']  # Get memory used as percentage
                        powered_on_vms.append((vmid, mem))  # Return VM ID, actual memory used, allocated memory
                except Exception as e:
                    print(f"Failed to retrieve status for VM {vmid}: {e}")
            return powered_on_vms

        # Iterate over each node and retrieve VM memory stats
        for node in node_stats:
            # Print the node name
            print(f"Node: {node}", end=", ")

            # Get the powered-on VMs and their memory usage
            powered_on_vms = get_powered_on_vms(node)

            # Print the actual memory usage of each VM as 'used/allocated', separated by commas
            vm_memory_list = [f"{vm[1]:.2f}" for vm in powered_on_vms]  # Format as 'used/allocated'
            print(", ".join(vm_memory_list))  # Join and print the memory usage separated by commas

    def get_buckets(self, host_names=None):
        """
        Get buckets for the specified host names, sorted by node name.
        
        :param host_names: List of host names to include. If None, include all hosts.
        :return: List of buckets with VMs and static items.
        """
        # Fetch node usage stats from Proxmox
        node_stats = self.get_node_usage()

        # Filter the node stats based on the provided host names
        if host_names:
            node_stats = {node: stats for node, stats in node_stats.items() if node in host_names}

        # Sort the nodes by name
        sorted_node_names = sorted(node_stats.keys())

        # Create buckets with initial loads and include hostnames
        buckets_initial = []
        for i, node in enumerate(sorted_node_names):
            # Initialize the bucket with the node's capacity and hostname
            bucket = Bucket(i, node_stats[node]['max_memory'], hostname=node)
            
            # Add static item for system memory that cannot be moved
            system_memory_used = node_stats[node]['memory_used'] - sum([vm['memory_used'] for vm in self.get_powered_on_vms(node)])
            static_item = Item(f"{node}-static", bucket, system_memory_used, movable=False)
            bucket.add_item(static_item)

            # Add dynamic items for each powered-on VM
            powered_on_vms = self.get_powered_on_vms(node)
            for vm in powered_on_vms:
                vmid = vm['vmid']
                memory_used = vm['memory_used']  # VM memory used in GB
                dynamic_item = Item(vmid, bucket, memory_used, movable=True)
                bucket.add_item(dynamic_item)

            # Append the bucket to the initial list
            buckets_initial.append(bucket)

        return buckets_initial