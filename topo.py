
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.examples.linuxrouter import LinuxRouter
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import argparse
import time


class TopoSecu(Topo):

    def build(self):

        # Add 2 routers in two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip=None)  # Workstation LAN router
        r2 = self.addHost('r2', cls=LinuxRouter, ip=None)  # Internet router

        # Add 2 switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add router-switch links in the same subnet
        self.addLink(s1, r1, intfName2='r1-eth0', params2={'ip': '10.1.0.1/24'})
        self.addLink(s2, r1, intfName2='r1-eth12', params2={'ip': '10.12.0.1/24'})
        self.addLink(s2, r2, intfName2='r2-eth12', params2={'ip': '10.12.0.2/24'})

        # Add outside host
        internet = self.addHost(name='internet', ip='10.2.0.2/24', defaultRoute='via 10.2.0.1')
        self.addLink(internet, r2, intfName2='r2-eth0', params2={'ip': '10.2.0.1/24'})

        # Adding hosts specifying the default route
        ws2 = self.addHost(name='ws2', ip='10.1.0.2/24', defaultRoute='via 10.1.0.1')
        ws3 = self.addHost(name='ws3', ip='10.1.0.3/24', defaultRoute='via 10.1.0.1')
        httpServer = self.addHost(name='http', ip='10.12.0.10/24', defaultRoute='via 10.12.0.2')
        dnsServer = self.addHost(name='dns', ip='10.12.0.20/24', defaultRoute='via 10.12.0.2')
        ntpServer = self.addHost(name='ntp', ip='10.12.0.30/24', defaultRoute='via 10.12.0.2')
        ftpServer = self.addHost(name='ftpHost', ip='10.12.0.40/24', defaultRoute='via 10.12.0.2')

        # Add host-switch links
        self.addLink(ws2, s1)
        self.addLink(ws3, s1)
        self.addLink(httpServer, s2)
        self.addLink(dnsServer, s2)
        self.addLink(ntpServer, s2)
        self.addLink(ftpServer, s2)


topos = {
    "secu": ( lambda: TopoSecu() )
}


def add_routes(net):
    ### STATIC ROUTES ###
    info(net['r1'].cmd("ip route add 10.2.0.0/24 via 10.12.0.2 dev r1-eth12"))
    info(net['r2'].cmd("ip route add 10.1.0.0/24 via 10.12.0.1 dev r2-eth12"))


def start_services(net):
    # Apache2 HTTP server
    info(net['http'].cmd("/usr/sbin/apache2ctl -DFOREGROUND &"))
    # dnsmasq DNS server
    info(net['dns'].cmd("/usr/sbin/dnsmasq -k &"))
    # NTP server
    info(net['ntp'].cmd("/usr/sbin/ntpd -d &"))
    # ftpHost server
    info(net['ftpHost'].cmd("/usr/sbin/vsftpd &"))


def stop_services(net):
    # Apache2 HTTP server
    info(net['http'].cmd("killall apache2"))
    # dnsmasq DNS server
    info(net['dns'].cmd("killall dnsmasq"))
    # ftpHost server
    info(net['ftpHost'].cmd("killall vsftpd"))
    
def configure_firewall(net):
    r1 = net['r1']
    r2 = net['r2']

    dmz_servers =[net['http'],net['ntp'],net['ftpHost'],net['dns']]

    # Flush existing rules
    r1.cmd('nft flush ruleset')
    r2.cmd('nft flush ruleset')

    # Create tables and chains
    r1.cmd('nft add table inet filter')
    r1.cmd("nft add chain inet filter input '{ type filter hook input priority 0; }'")
    r1.cmd("nft add chain inet filter forward '{ type filter hook forward priority 0; }'")

    r2.cmd('nft add table inet filter')
    r2.cmd("nft add chain inet filter input '{ type filter hook input priority 0; }'")
    r2.cmd("nft add chain inet filter forward '{ type filter hook forward priority 0; }'")

    # Workstation policies
    r1.cmd('nft add rule inet filter forward ip saddr 10.1.0.0/24 ct state new accept')
    r1.cmd('nft add rule inet filter forward ip saddr 10.1.0.0/24 icmp type echo-request accept')
    
    # DMZ server policies
    for dmz in dmz_servers:
        dmz.cmd('nft add table inet filter')
        dmz.cmd("nft add chain inet filter input '{ type filter hook input priority 0; }'")
        #dmz.cmd('nft add rule inet filter input ip saddr 10.12.0.0/24 drop')
        dmz.cmd("nft add rule inet filter forward ip saddr 10.12.0.0/24 icmp type echo-request drop")

    
    # R1/R2 rules for DMZ  
    r1.cmd("nft add rule inet filter forward ip saddr 10.12.0.0/24 icmp type echo-request drop")
    r2.cmd("nft add rule inet filter forward ip saddr 10.12.0.0/24 icmp type echo-request drop")
    r1.cmd("nft add rule inet filter forward ip saddr 10.12.0.0/24 ct state new drop")
    r2.cmd("nft add rule inet filter forward ip saddr 10.12.0.0/24 ct state new drop")
    # Internet policies
    r2.cmd('nft add rule inet filter forward ip saddr 10.2.0.2 ip daddr 10.12.0.0/24 ct state new accept')
    r2.cmd('nft add rule inet filter forward ip saddr 10.2.0.2 ip daddr 10.12.0.0/24 icmp type echo-request accept')
    r2.cmd('nft add rule inet filter forward ip saddr 10.2.0.2 ip daddr 10.1.0.0/24 ct state new drop')
    r2.cmd('nft add rule inet filter forward ip saddr 10.2.0.2 ip daddr 10.1.0.0/24 icmp type echo-request drop')


def run():
    topo = TopoSecu()
    net = Mininet(topo=topo)

    add_routes(net)
    stop_services(net)
    time.sleep(1)
    start_services(net)

    net.start()
    #configure_firewall(net)
    CLI(net)
    stop_services(net)
    net.stop()


def ping_all():
    topo = TopoSecu()
    net = Mininet(topo=topo)
    add_routes(net)
    stop_services(net)
    time.sleep(1)
    start_services(net)

    net.start()
    net.pingAll()
    stop_services(net)
    net.stop()


if __name__ == '__main__':

    # Command-line arguments
    parser = argparse.ArgumentParser(
        prog="topo.py",
        description="Mininet topology for the network attacks project of the course LINFO2347."
    )
    # Optional flag -p
    parser.add_argument("-p", "--pingall", action="store_true", help="Perform pingall test")
    # Parse arguments
    args = parser.parse_args()

    setLogLevel('info')

    if args.pingall:
        # Deploy topology, run pingall test, then exit
        ping_all()
    else:
        # Deploy topology, open CLI
        run()
        
        
