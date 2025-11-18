#!/bin/bash
# Deploy Omarchy Advanced updates to VM - ONE COMMAND, ONE PASSWORD
# Usage: ./scripts/deploy-to-vm.sh <vm-ip-address> [ssh-user] [component]
# Example: ./scripts/deploy-to-vm.sh 192.168.50.73 steve
# Example: ./scripts/deploy-to-vm.sh 192.168.50.73 steve greetd
# Components: wayvnc (default), greetd, all, logs

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
  echo "  partition        - Deploy updated partition-selection assets"
  echo "  all              - Deploy both wayvnc and greetd"
  echo ""
  echo " -- independent PULL ACTIONS -- "
  echo "  logs             - IMPORT logs from VM to current project /logs folder"
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

  # Copy greetd config update script to VM
  scp $SSH_OPTS -q scripts/update-greetd-config.sh "$SSH_USER@$VM_IP:/tmp/update-greetd-config.sh"
  echo "✓ greetd config script copied to /tmp on VM"

  # Update greetd sway-config with session restriction
  echo "Updating greetd sway-config..."
  ssh $SSH_OPTS -t "$SSH_USER@$VM_IP" sudo bash /tmp/update-greetd-config.sh
  echo "✓ greetd configuration updated"

  # Copy and execute omarchy-advanced.desktop fix script
  scp $SSH_OPTS -q scripts/fix-omarchy-advanced-session.sh "$SSH_USER@$VM_IP:/tmp/fix-omarchy-advanced-session.sh"
  echo "Fixing omarchy-advanced.desktop Exec line..."
  ssh $SSH_OPTS -t "$SSH_USER@$VM_IP" sudo bash /tmp/fix-omarchy-advanced-session.sh
}


# Function to deploy partition selection updates
deploy_partition_selection() {
  echo ""
  echo "Deploying partition selection assets..."

  # Copy all files (reuses SSH session, no password needed)
  scp $SSH_OPTS -q bin/omarchy-partition-select "$SSH_USER@$VM_IP:/root/omarchy/bin/omarchy-partition-select"
  scp $SSH_OPTS -q bin/omarchy-partition-select-revised "$SSH_USER@$VM_IP:/root/omarchy/bin/omarchy-partition-select-revised"
  scp $SSH_OPTS -q ../omarchy-advanced-iso/configs/airootfs/root/configurator "$SSH_USER@$VM_IP:/root/configurator"
  scp $SSH_OPTS -q ./scripts/setup-partition-test-disk.sh "$SSH_USER@$VM_IP:/root/omarchy/scripts/setup-partition-test-disk.sh"
  echo "✓ Files copied to VM"

}
# Function to copy logs from VM to local logs folder
copy_logs_from_vm() {
  echo ""
  echo "Copying logs from VM..."

  # Copy all files (reuses SSH session, no password needed)
  scp $SSH_OPTS -q "$SSH_USER@$VM_IP:/var/log/omarchy-install.log" ./logs/omarchy-install.log
  scp $SSH_OPTS -q "$SSH_USER@$VM_IP:/tmp/configurator.log" ./logs/configurator.log
  scp $SSH_OPTS -q "$SSH_USER@$VM_IP:/tmp/partition-select.log" ./logs/partition-select.log
  echo "✓ Files copied to /logs in project folder"

}

# Deploy based on component selection
case "$COMPONENT" in
  wayvnc)
    deploy_wayvnc
    ;;
  greetd)
    deploy_greetd
    ;;
  partition)
    deploy_partition_selection
	;;
  logs)
    copy_logs_from_vm
	;;
  all)
    deploy_wayvnc
    deploy_greetd
	deploy_partition_selection
    ;;
  *)
    echo "ERROR: Unknown component '$COMPONENT'"
    echo "Valid options: wayvnc, greetd, all, logs"
    exit 1
    ;;
esac

# Cleanup control socket
rm -f "$CONTROL_SOCKET"

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
