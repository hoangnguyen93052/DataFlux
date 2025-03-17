import socket
import threading
import pickle
import os
import time

class Peer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.peers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.running = True

    def start(self):
        print(f"Peer started at {self.host}:{self.port}")
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        threading.Thread(target=self.broadcast_presence, daemon=True).start()

    def listen_for_messages(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = pickle.loads(data)
                if message['type'] == 'discovery':
                    self.handle_discovery(message, addr)
                elif message['type'] == 'message':
                    self.handle_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")

    def broadcast_presence(self):
        while self.running:
            self.send_message({'type': 'discovery', 'address': (self.host, self.port)})
            time.sleep(5)

    def send_message(self, message, target=None):
        message_data = pickle.dumps(message)
        if target:
            self.sock.sendto(message_data, target)
        else:
            for peer in self.peers:
                self.sock.sendto(message_data, peer)

    def handle_discovery(self, message, addr):
        if addr not in self.peers:
            print(f"Discovered new peer: {addr}")
            self.peers.append(addr)
            self.send_message({'type': 'response', 'address': (self.host, self.port)}, addr)

    def handle_message(self, message):
        print(f"Message from peer: {message['content']}")
        if message.get('response_to'):
            print(f"Response to: {message['response_to']}")

    def stop(self):
        self.running = False
        self.sock.close()
        print("Peer stopped")

class UserInterface:
    def __init__(self, peer):
        self.peer = peer

    def run(self):
        while True:
            command = input("Enter command (send/exit): ")
            if command == 'send':
                content = input("Enter message to send: ")
                self.peer.send_message({'type': 'message', 'content': content})
            elif command == 'exit':
                self.peer.stop()
                break
            else:
                print("Unknown command. Please try again.")

if __name__ == "__main__":
    peer = Peer(host='127.0.0.1', port=5000)
    peer.start()
    interface = UserInterface(peer)
    interface.run()