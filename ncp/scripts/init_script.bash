#!/bin/bash

# -------------- Mount drive --------------

# Variables
DEVICE="/dev/xvdb"
MOUNT_POINT="/home"
FILESYSTEM="ext4"

# Step 1: Format the drive
echo "Formatting $DEVICE with $FILESYSTEM..."
sudo mkfs.$FILESYSTEM -F $DEVICE
if [ $? -ne 0 ]; then
    echo "Failed to format $DEVICE. Exiting."
    exit 1
fi

# Step 2: Get the UUID of the drive
UUID=$(sudo blkid -s UUID -o value $DEVICE)
if [ -z "$UUID" ]; then
    echo "Failed to retrieve UUID for $DEVICE. Exiting."
    exit 1
fi
echo "UUID for $DEVICE is $UUID."

echo "Mounting $DEVICE to $MOUNT_POINT..."
sudo mount $DEVICE $MOUNT_POINT

# Step 6: Backup /etc/fstab
echo "Backing up /etc/fstab to /etc/fstab.bak..."
sudo cp /etc/fstab /etc/fstab.bak

# Step 7: Add entry to /etc/fstab for persistent mount
FSTAB_ENTRY="UUID=$UUID $MOUNT_POINT $FILESYSTEM defaults 0 2"
if ! grep -q "$UUID" /etc/fstab; then
    echo "Adding new entry to /etc/fstab: $FSTAB_ENTRY"
    echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab
else
    echo "Entry for UUID $UUID already exists in /etc/fstab. Skipping."
fi

# Step 8: Verify the mount
echo "Verifying that $DEVICE is mounted at $MOUNT_POINT..."
df -h | grep $MOUNT_POINT

echo "Setup completed successfully. $DEVICE is now mounted at $MOUNT_POINT and will persist across reboots."

# -------------- Setup user --------------

USERNAME="chan"
PASSWORD="passwordtemp"
PUBLIC_KEYS=$(cat <<'EOF'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHgxTXJNVOpoNB2Fp3s+k7i5IA2rGQla9cb8XIMnK2g9X8VeOSN1CJKBiw25fo+pmD61MGZeI8fRjFe1VOGC+7ntwzAE0MKOtoOHWcNvs8oZU/sRa02iDIo4w5I16PYqkBEtZBrdmG2UTZWtmBYa7X4xpa9KCG88XKXIcn2xX4ap0bWQBPxdfZEH00dBoOQ+z7DhKz99QBAZJHfN2/on19QuHJEbytzK+BkAIGPzezmqrrpELQOr3cfQlRQNsISjOzJORiOBqUhhQGQqwHhy/J+bUwFvjLmKfb+qY0CSH8Tl7wQ1bXZ0vG/nSsLOj5fVUxHAaMxfBZKV+kI5B26lcqfd2iRLay8vKfUsO3jPyQp+rorOVE0rebTjTlBEoxs8EzSTNmbxNFh3wp4S0VfNlaufj4bpRHHGWoWDKywZIUecGr/3UQr3V94KWQJyB2Dq1/seqUtAlmdwQUzTUepKg9WZpC7/bVPwX6PlA4XdtpnfFcAVuE6R5xN2CxGijTP0M= chanyoungs@OMEN
ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAuMeFmXKZ2djYSULXXHFDSZbWbrX074NyJocVJWMCEX56OGyQby4ND4p8yxGAzkscULsXu7Wg4lQXayc77REVYwK/j7D6AfZlptpjM6sVHoGwgLwIWhjEoLXk07wLmU7n2tptXtdWsO0wUlSEPVqwIn+2AlqF8heu2PCGwPhHD6btLD7LbYVpNe12Q1EbC/EyhXh408VXbP+/jmHFjtqZT1KPfA4EY+KwUiL2z8SmZAwC1uWnX0YwJVDCx5cwrP0FPxextI7Hmp3ddRbHHKOtSZNroXw8hyIO/EbDrLwlc6MiPpwTIIjyEj6M+5prmdN0X6ulR0ok32Df1VZHVn+Miw== rsa-key-20170503
EOF
)
SSH_DIR="/home/$USERNAME/.ssh"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"
SSHD_CONFIG="/etc/ssh/sshd_config"

# Add user non-interactively
echo "Creating user $USERNAME..."
sudo useradd -m -s /bin/bash -G sudo $USERNAME

# Set password for the user
echo "$USERNAME:$PASSWORD" | sudo chpasswd

# Set up SSH directory and authorized_keys for the new user
echo "Setting up SSH for $USERNAME..."
sudo mkdir -p $SSH_DIR
sudo echo "$PUBLIC_KEY" | sudo tee $AUTHORIZED_KEYS > /dev/null
sudo chmod 700 $SSH_DIR
sudo chmod 600 $AUTHORIZED_KEYS
sudo chown -R $USERNAME:$USERNAME $SSH_DIR

# Configure SSH server to allow key-based login and disable password login
echo "Configuring SSH server..."
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' $SSHD_CONFIG
sudo sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' $SSHD_CONFIG

# Restart SSH service
echo "Restarting SSH service..."
sudo systemctl restart ssh

echo "Setup completed. User $USERNAME can now log in using the SSH key."

# -------------- Install packages --------------
sudo apt-get install nvtop -y
sudo apt-get install ffmpeg -y