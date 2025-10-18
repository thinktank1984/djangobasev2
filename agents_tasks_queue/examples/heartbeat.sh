#!/bin/bash
echo "Heartbeat at $(date)"
echo "System status: $(uptime)"
echo "Memory usage: $(free -h | grep Mem)"
echo "Disk usage: $(df -h . | tail -1)"