#!/bin/bash

# Ask for the username
num_users=1
# Get random usernames and passwords
mapfile -t usernames < <(shuf -n $num_users usernames50.txt)
mapfile -t passwords < <(shuf -n $num_users rockyou50.txt)

for i in ${!usernames[@]}; do
    username=${usernames[$i]}
    password=${passwords[$i]}
    echo $username
    echo $password
    # Print the username and password
    sudo useradd -m $username
    echo "$username:$password" | sudo chpasswd
    # Set up the FTP directory
    sudo mkdir /home/$username/ftp
    sudo chown nobody:nogroup /home/$username/ftp
    sudo chmod a-w /home/$username/ftp

    # Set up the FTP directory for uploading files
    sudo mkdir /home/$username/ftp/upload
    sudo chown $username:$username /home/$username/ftp/upload

    # Configure vsftpd for the new user
    echo "user_sub_token=$username
    local_root=/home/$username/ftp
    user_config_dir=/etc/vsftpd/user_config_dir" | sudo tee -a /etc/vsftpd.conf > /dev/null
done
# Create the new user and set its password


# Restart vsftpd service
sudo systemctl restart vsftpd
