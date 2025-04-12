#!/bin/bash

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

# Setup Script for ProxmoxLoadBalancer
#
# Instructions:
#   1. Ensure you have created the proper API user in your Proxmox cluster.
#   2. Adjust any credentials in LoadBalancer.py as needed.
#
# This script will:
#   - Install Python dependencies.
#   - Move the entire repository to /opt/ProxmoxLoadBalancer.
#   - Copy the systemd service and timer files to /etc/systemd/system.
#   - Reload systemd and enable/start the timer.
#
# Usage:
#   chmod +x setup.sh
#   sudo ./setup.sh
#

# Check if the script is run as root
if [[ "$EUID" -ne 0 ]]; then
  echo "Please run as root"
  exit 1
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Copying repository to /opt/ProxmoxLoadBalancer..."
# Remove any previous installation (optional)
if [ -d /opt/ProxmoxLoadBalancer ]; then
  echo "/opt/ProxmoxLoadBalancer already exists. Removing old directory."
  rm -rf /opt/ProxmoxLoadBalancer
fi

# Copy the entire repository directory to /opt/
cp -R . /opt/ProxmoxLoadBalancer

# Ensure that the main file is executable
chmod +x /opt/ProxmoxLoadBalancer/LoadBalancer.py

echo "Copying systemd service and timer files..."
# Copy the systemd service and timer files to the proper location
cp loadbalancer.service /etc/systemd/system/loadbalancer.service
cp loadbalancer.timer /etc/systemd/system/loadbalancer.timer

echo "Setting up systemd services..."
# Reload systemd to register the new service and timer
systemctl daemon-reload

# Enable and start the timer to schedule the load balancer
systemctl enable loadbalancer.timer
systemctl start loadbalancer.timer

echo "ProxmoxLoadBalancer setup is complete!"
