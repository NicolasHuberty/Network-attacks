# Project Network Attacks
*Huberty Nicolas and Tourpe Romain*

## Initial firewall
To launch the inital firewall, you have to run the command : `r1 nft -f Network-attacks/FirewallRules/basicFirewallr1.nft` and `r2 nft -f Network-attacks/FirewallRules/basicFirewallr2.nft`
In this firewall we have implemented:
1. Workstations can send ping and initiate a connection towards any other host. We did not have to write any rule for this one since we don't have to filter anything.
2. DMZ servers cannot send any ping or initiate any connection. So we wrote a rule on r2 since all the traffic from the DMZ is directed to r2. In this rule, we block every outgoing ICMP or new connection request from the DMZ.
3. The Internet can send a ping or initiate a connection only towards DMZ servers. We wrote a rule on r1 and r2 to block every ICMP and new incoming connection from the internet. 
## Flooding attack

**Attack**
We implemented a SYN flooding attack. For this attack, we send SYN packets from the internet to the HTTP service. 
To run this attack, you have to type `internet python3 Network-attacks/Attacks/FloodingAttack.py`. After a short time, you will see that the HTTP sevrer cannot respond to any connection anymore.
This attack has been implemented by sending ip/tcp/raw packets in a loop, with multiples threads. In the meantime, we check the RTT every 3 seconds to verify wheter the service is still able to answer or not.
**Means of protection**
Since this attack is based on sending a lot of SYN packets from the internet, we decided to limit on r2 the amount of SYn packets one can send from the internet to a DMZ. You can activate this protection by typing `r2 nft -f Network-attacks/FirewallRules/floodingAttackFirewallr2.nft`
## FTP bruteforce attack

**Attack** 
For the second attack, we choosed to implement a FTP bruteforce attack based on dictionary. First, we have to add some user to the FTP service. To do so, we created a small bash script that creates one single user. The right command to execute is : `sudo ./Network-attacks/createFTPuser.sh`. For the purpose of the demonstration, we choose both the username and the password in a dictionary. We could have decided to add a user with a random name and a random password but then the bruteforce would have take forever. The next step is then to launch the attack. We launch this attack from internet : `internet python3 ./Network-attacks/Attacks/FTPBruteForce.py`. If you have a lot of time, you can chose a longer dictionary but we decided to only use the 50 first password and 50 first username to go faster. The code will then try each username:password combinaison until it found the right one.
**Means of protection**
Since this attack is based on sending a lot of packets to the port 21 (SSH/FTP) and try to create a new connection each time we try a new username:password combinaison, we decided to limit the number of packet you can send per minute. With the protection `r2 nft -f Network-attacks/FirewallRules/fTPBruteForceFirewallr2.nft`, you now have a protection against bruteforce attack by limiting the amount of packets one can send. Now, if you try this attack once again, you will have most of your packets dropped.
## Network scan

**Attack** 
The third attack is a Network scan. For this one, we scan every address on the 10.12.0.0/24 and 10.1.0.0/24 subnetworks. We tried to scan everything on the 10.0.0.0/8 subnetwork but it takes way too long (+16 million attempts/packets to send). We analyze the network by sending ip/tcp/raw packets to each address and waiting for a reponse (or not). After analyzing the different RTT in the network, we saw that in was in average 0.05s, so we decided for this attack to use a timeout of 1s to be sure. In order to launch this attack, you have to type the `ws2 python3 ./Network-attacks/Attacks/NetworkScan.py`.
**Means of protection**
As a mean of protection, since this attack is based as sending a lot of SYN packets trough r1 and see if someone respond, we limit the rate of new connection packets. If there is more than 50 packets send per minte, r1 will start dropping the exceeding packets, and there will never be a response. To activate this mean of protection, you have to type `r1 nft -f Network-attacks/FirewallRules/networkScanFirewallr1.nft`

