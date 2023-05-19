from scapy.all import sr, IP, UDP, ICMP, TCP
import ipaddress
import threading

network = "10.12.0.0/24"
network2 = "10.1.0.0/24"
ports = [1,7, 19, 20, 21, 22, 23, 25, 42, 43, 49, 53, 67, 68, 69, 70, 79, 80, 88, 102, 110, 113, 119, 123, 135, 137, 138, 139, 143, 161, 162, 177, 179, 194, 201, 264, 318, 381,
         383, 389, 411, 412, 427, 443, 445, 464, 465, 497, 500, 512, 513, 514, 515, 520, 521, 540, 548, 554, 546, 547, 560, 563, 587, 591, 593, 596, 631, 636, 639, 646, 691, 860,
         873, 902, 989, 990, 993, 995, 1025, 1026, 1027, 1028, 1029, 1080, 1194, 1214, 1241, 1311, 1337, 1589, 1701, 1720, 1723, 1725, 1741, 1755, 1812, 1813, 1863, 1900, 1985,
         2000, 2002, 2049, 2082, 2083, 2100, 2222, 2302, 2483, 2484, 2745, 2967, 3050, 3074, 3127, 3128, 3222, 3260, 3306, 3389, 3689, 3690, 3724, 3784, 3785, 4333, 4444, 4500,
         4664, 4672, 4899, 5000, 5001, 5004, 5005, 5050, 5060, 5061, 5190, 5222, 5223, 5353, 5432, 5554, 5631, 5632, 5800, 5900, 5901, 5902, 5903, 5904, 5905, 5906, 5907, 5908,
         5909, 5910, 5911, 5912, 5913, 5914, 5915, 5916, 5917, 5918, 5919, 5920, 5921, 5922, 5923, 5924, 5925, 5926, 5927, 5928, 5929, 5930, 5931, 5932, 5933, 5934, 5935, 5936,
         5937, 5938, 5939, 5940, 5941, 5942, 5943, 5944, 5945, 5946, 5947, 5948, 5949, 5950, 5951, 5952, 5953, 5954, 5955, 5956, 5957, 5958, 5959, 5960,5900, 5999, 6000, 6001,
         6112, 6129, 6257, 6346, 6347, 6379, 6500, 6566, 6588, 6665, 6669, 6679, 6697, 6699, 6881, 6999, 6891, 6901, 6970, 7000, 7001, 7199, 7648, 7649, 8000]
class PortScanner:
    def __init__(self, ip_list, ports):
        self.ip_list = ip_list
        self.ports = ports

    def print_service(self, ip, port, protocol):
        services = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",5353:"DNS", 80: "HTTP", 443: "HTTPS",123:"NTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL"}
        service = services.get(port)
        if service:
            print(f"{protocol} Service detected on {ip}:{port}. Could be a {service} server.")

    def scan_ports(self, ip):
        print(ip)
        tcp_packets = [IP(dst=ip)/TCP(dport=port, flags="S") for port in self.ports]
        udp_packets = [IP(dst=ip)/UDP(dport=port) for port in self.ports]
        responses, unanswered = sr(tcp_packets + udp_packets, timeout=1, verbose=0)
        workstations = dict()
        ip_service_detected = dict()
        for response in responses:
            sent_packet, received_packet = response
            if sent_packet.haslayer(TCP):
                if received_packet[TCP].flags == "SA":
                    self.print_service(ip, sent_packet[TCP].dport, "TCP")
                    ip_service_detected[ip] = True
                else:
                    workstations[ip] = True
            elif sent_packet.haslayer(UDP):
                if not received_packet.haslayer(ICMP): 
                    self.print_service(ip, sent_packet[UDP].dport, "UDP")
                    ip_service_detected[ip] = True

        if ip not in ip_service_detected and ip in workstations:
            print(f"Workstation detected: {ip}")

    def start_scan(self):
        semaphore = threading.Semaphore(2)
        def thread_target(ip):
            with semaphore:
                self.scan_ports(ip)
        threads = [threading.Thread(target=thread_target, args=(ip,)) for ip in self.ip_list]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

def generate_ip_list(network):
    ip_network = ipaddress.ip_network(network)
    return [str(ip) for ip in ip_network.hosts()]

if __name__ == "__main__":
    ip_list = generate_ip_list(network) + generate_ip_list(network2)
    scanner = PortScanner(ip_list, ports)
    scanner.start_scan()
