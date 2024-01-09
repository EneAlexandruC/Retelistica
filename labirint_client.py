import socket

class Maze():
    def __init__(self, server_addr="127.0.0.1", server_port=5566):
        self.server_addr = server_addr
        self.server_port = server_port
    
    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_addr, self.server_port))

        while True:
            #comanda de la client pentru a se muta in labirint
            command = str(input())

            client.send(command.encode("utf-8"))
            server_message = client.recv(1024).decode("utf-8")
            
            print(server_message)

            if server_message == "La revedere!":
                break

if __name__ == '__main__':
    client = Maze()
    client.start()