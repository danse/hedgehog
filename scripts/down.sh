#!/usr/bin/env bash
# Stop SuperDirt and the SuperCollider server started by this project.
set -u
echo "Stopping SuperDirt / scsynth..."
pkill -u "$USER" -f 'sclang.*BootSuperDirt.scd' 2>/dev/null && echo "  sclang stopped" || echo "  no sclang"
sleep 1
pkill -u "$USER" -x scsynth 2>/dev/null && echo "  scsynth stopped" || echo "  no scsynth"
rm -f "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/logs/superdirt.pid"
