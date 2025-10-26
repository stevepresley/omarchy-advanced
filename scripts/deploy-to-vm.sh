#!/bin/bash
# Deploy Omarchy Advanced updates to VM - ONE COMMAND, ONE PASSWORD
# Usage: ./scripts/deploy-to-vm.sh <vm-ip-address> [ssh-user] [component]
# Example: ./scripts/deploy-to-vm.sh 192.168.50.73 steve
# Example: ./scripts/deploy-to-vm.sh 192.168.50.73 steve greetd
# Components: wayvnc (default), greetd, all

set -e

# Get VM IP, SSH user, and component from arguments
VM_IP="${1:-}"
SSH_USER="${2:-steve}"
COMPONENT="${3:-wayvnc}"

if [[ -z "$VM_IP" ]]; then
  echo "Usage: $0 <vm-ip-address> [ssh-user] [component]"
  echo "Example: $0 192.168.50.73 steve"
  echo "Example: $0 192.168.50.73 steve greetd"
  echo ""
  echo "Components:"
  echo "  wayvnc (default) - Deploy wayvnc monitor service"
  echo "  greetd           - Reconfigure greetd display manager"
  echo "  all              - Deploy both wayvnc and greetd"
  exit 1
fi

# Setup SSH control socket for connection multiplexing
# This allows all SSH/SCP commands to reuse the same authenticated session
CONTROL_SOCKET="/tmp/ssh-deploy-${SSH_USER}-${VM_IP}"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$CONTROL_SOCKET -o ControlPersist=5m"

echo "Establishing SSH connection (you will enter password once)..."
ssh $SSH_OPTS -o ConnectTimeout=5 "$SSH_USER@$VM_IP" "echo 'SSH OK'" || {
  echo "ERROR: Cannot connect to $VM_IP via SSH"
  exit 1
}
echo "✓ SSH connection established"

# Function to deploy wayvnc monitor
deploy_wayvnc() {
  echo ""
  echo "Deploying wayvnc monitor..."

  # Copy all files (reuses SSH session, no password needed)
  scp $SSH_OPTS -q install/files/usr-local-bin-omarchy-wayvnc-monitor "$SSH_USER@$VM_IP:/tmp/omarchy-wayvnc-monitor"
  scp $SSH_OPTS -q config/systemd/system/omarchy-wayvnc-monitor.service "$SSH_USER@$VM_IP:/tmp/omarchy-wayvnc-monitor.service"
  scp $SSH_OPTS -q scripts/deploy-wayvnc-monitor.sh "$SSH_USER@$VM_IP:/tmp/deploy-wayvnc-monitor.sh"
  echo "✓ Files copied to /tmp on VM"

  # Execute deployment script (reuses SSH session)
  ssh $SSH_OPTS -t "$SSH_USER@$VM_IP" sudo bash /tmp/deploy-wayvnc-monitor.sh
  echo "✓ wayvnc monitor deployed"
}

# Function to deploy greetd configuration
deploy_greetd() {
  echo ""
  echo "Deploying greetd configuration..."

  # Copy greetd installation script to VM
  scp $SSH_OPTS -q install/login/greetd.sh "$SSH_USER@$VM_IP:/tmp/greetd-update.sh"
  echo "✓ greetd script copied to /tmp on VM"

  # Stop greetd service, reconfigure, and restart
  echo "Reconfiguring greetd..."
  ssh $SSH_OPTS -t "$SSH_USER@$VM_IP" bash -c '
    set -e
    echo "Stopping greetd service..."
    sudo systemctl stop greetd.service || true
    echo "Running greetd configuration..."
    sudo bash /tmp/greetd-update.sh
    echo "Starting greetd service..."
    sudo systemctl start greetd.service
    echo "✓ greetd reconfigured and restarted"
  '
}

# Deploy based on component selection
case "$COMPONENT" in
  wayvnc)
    deploy_wayvnc
    ;;
  greetd)
    deploy_greetd
    ;;
  all)
    deploy_wayvnc
    deploy_greetd
    ;;
  *)
    echo "ERROR: Unknown component '$COMPONENT'"
    echo "Valid options: wayvnc, greetd, all"
    exit 1
    ;;
esac

# Cleanup control socket
rm -f "$CONTROL_SOCKET"

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
