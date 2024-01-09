import random as rd
import queue
import socket

class Maze():
    def __init__(self, port=5566):
        self.server_port = port
        self.maze, self.exit_position = self.generate_maze()
        self.player_position, self.monster_position = self.generate_players_position()
    
    # metoda care alege aleatoriu unu din cele 5 fisiere cu modele de labirint si il incarca in memoria server-ului
    def generate_maze(self):
        maze = [[' ' for _ in range(10)] for _ in range(10)]
        exit_position = []

        choice = rd.randint(0,4)
        file_path = "resources\\models\\maze" + str(choice) + ".txt"

        with open(file_path, 'r') as input_file:
            for row in range(10):
                data = input_file.readline()
                for index in range(10):
                    if data[index*2] == '#':
                        maze[row][index] = '#'
                    if ((row == 0 or row == 9) and data[index*2] == ' ') or ((index == 0 or index == 9) and data[index*2] == ' '):
                        exit_position.append(row)
                        exit_position.append(index)
        
        # ! pentru debugg !
        # for row in maze:
        #     print(' '.join(row))
        # print(exit_position)

        return maze, exit_position
    

    # pentru a determina daca monstrul generat sta in calea jucatorului, se va realiza o parcurgere BFS
    def is_exit_reachble(self, playerX ,playerY):
        #initializaera matricii de vizitare
        vizitat = [[0 for _ in range(10)] for _ in range(10)]

        #vectori de pozitie
        dx = [-1, 0, 1, 0]
        dy = [0, 1, 0, -1]


        for i in range(10):
            for j in range(10):
                if (self.maze[i][j] == '#'):
                    vizitat[i][j] = 1
        
        #marcam pozitita player-ului ca fiind vizitata, totodata marcam si punctul de plecare
        vizitat[playerX][playerY] = 1

        q = queue.Queue()
        q.put([playerX, playerY])

        while not q.empty():
            
            #se extrage primul element din coada si se stocheaza intr-o variabila
            coords = q.get()

            for i in range(4):
                if vizitat[coords[0] + dx[i]][coords[1] + dy[i]] == 0 and self.maze[coords[0] + dx[i]][coords[1] + dy[i]] != 'M':
                    
                    #cazul in care coordonatele valide sunt chiar coordonatele iesirii
                    if coords[0] + dx[i] == self.exit_position[0] and coords[1] + dy[i] == self.exit_position[1]:
                        return True
                    q.put([coords[0] + dx[i], coords[1] + dy[i]])
                    vizitat[coords[0] + dx[i]][coords[1] + dy[i]] = 1
            
        return False
      

    def generate_players_position(self):

        # pentru a genera pozitia jucatorului am grija ca acesta sa fie la o distanta >= 3 mutari de iesire
        playerX = rd.randint(2,6)
        playerY = rd.randint(2,6)

        while self.maze[playerX][playerY] == '#':
            playerX = rd.randint(2,6)
            playerY = rd.randint(2,6)
        
        # pentru a genera pozitia monstrului se verifica regulile date in suportul de proiect (sa fie la 3 spatii distanta si sa nu 
        # blocheze calea jucatorului la iesire)
        monsterX = rd.randint(1,8)
        monsterY = rd.randint(1,8)

        while self.maze[monsterX][monsterY] == '#':
            monsterX = rd.randint(1,8)
            monsterY = rd.randint(1,8)
        self.maze[monsterX][monsterY] = 'M'

        # bucla unde se verifica conditiile
        while True:
            if monsterX <= playerX - 2 or monsterX >= playerX + 2:
                if monsterY <= playerY - 2 or monsterY >= playerY + 2:
                    if self.is_exit_reachble(playerX, playerY):
                        break
            self.maze[monsterX][monsterY] = ' '
            monsterX = rd.randint(1,8)
            monsterY = rd.randint(1,8)
            while self.maze[monsterX][monsterY] == '#':
                monsterX = rd.randint(1,8)
                monsterY = rd.randint(1,8)
            self.maze[monsterX][monsterY] = 'M'

        self.maze[playerX][playerY] = 'J'

        # ! pentru debugg !
        # for row in self.maze:
        #     print(' '.join(row))

        return [playerX, playerY], [monsterX, monsterY]
    
    def player_lost(self):
        for i in range(2):
            if self.player_position[i] != self.monster_position[i]:
                return False
        return True


    def start_game(self, client, server):
        moves = 0

        #mesajele catre client
        info_message_START = "Bine ai venit!\nControalele pentru a te misca prin labirint sunt urmatoarele:\nW-Sus\nS-Jos\nA-Stanga\nD-Dreapta"
        info_message_OK = "OK"
        info_message_PERETE = "Imposibil, ai lovit un perete. Încearcă altă directie."
        info_message_LOSE = "Ai picat pradă monstrului din labirint ... ai pierdut jocul. Încerca din nou!\nTasteaza 'START' pentru a reincepe jocul sau 'STOP' pentru a inchide conexiunea!."
        info_message_WRONG_INPUT = "Input gresit!\nControalele pentru a te misca prin labirint sunt urmatoarele:\nW-Sus\nS-Jos\nA-Stanga\nD-Dreapta"
        
        client.send(info_message_START.encode("utf-8"))
        
        #am scris o singura data comentariile deoarece acestea se repeda pentru fiecare dintre comenzile W, A, S, D
        while True:
            client_comand = client.recv(1024).decode("utf-8")

            if client_comand == 'S':
                if self.maze[self.player_position[0] + 1][self.player_position[1]] == ' ':
                    
                    #cazul in care playerul a ajuns la iesire
                    if self.player_position[0] + 1 == self.exit_position[0] and self.player_position[1] == self.exit_position[1]:
                        return moves + 1
                    #in caz contrar se va updata pozitia
                    else:
                        client.send(info_message_OK.encode("utf-8"))

                        #updatarea pozitiei in labirint
                        self.maze[self.player_position[0]][self.player_position[1]] = ' '
                        self.player_position[0] = self.player_position[0] + 1
                        moves += 1

                elif self.maze[self.player_position[0] + 1][self.player_position[1]] == '#':
                    client.send(info_message_PERETE.encode("utf-8"))
                    moves += 1
                #cazul in care playerul ajunge la monstru
                else:
                    client.send(info_message_LOSE.encode("utf-8"))
                    return
            elif client_comand == 'W':
                if self.maze[self.player_position[0] - 1][self.player_position[1]] == ' ':

                    if self.player_position[0] - 1 == self.exit_position[0] and self.player_position[1] == self.exit_position[1]:
                        return moves + 1
                    else:
                        client.send(info_message_OK.encode("utf-8"))

                        #updatarea pozitiei in labirint
                        self.maze[self.player_position[0]][self.player_position[1]] = ' '
                        self.player_position[0] = self.player_position[0] - 1
                        moves += 1

                elif self.maze[self.player_position[0] - 1][self.player_position[1]] == '#':
                    client.send(info_message_PERETE.encode("utf-8"))
                    moves += 1
                else:
                    client.send(info_message_LOSE.encode("utf-8"))
                    return
            elif client_comand == 'A':
                if self.maze[self.player_position[0]][self.player_position[1] - 1] == ' ':

                    if self.player_position[0] == self.exit_position[0] and self.player_position[1] - 1 == self.exit_position[1]:
                        return moves + 1
                    else:
                        client.send(info_message_OK.encode("utf-8"))

                        #updatarea pozitiei in labirint
                        self.maze[self.player_position[0]][self.player_position[1]] = ' '
                        self.player_position[1] = self.player_position[1] - 1
                        moves += 1

                elif self.maze[self.player_position[0]][self.player_position[1] - 1] == '#':
                    client.send(info_message_PERETE.encode("utf-8"))
                    moves += 1
                else:
                    client.send(info_message_LOSE.encode("utf-8"))
                    return
            elif client_comand == 'D':
                if self.maze[self.player_position[0]][self.player_position[1] + 1] == ' ':

                    if self.player_position[0] == self.exit_position[0] and self.player_position[1] + 1 == self.exit_position[1]:
                        return moves + 1
                    else:
                        client.send(info_message_OK.encode("utf-8"))

                        #updatarea pozitiei in labirint
                        self.maze[self.player_position[0]][self.player_position[1]] = ' '
                        self.player_position[1] = self.player_position[1] + 1
                        moves += 1

                elif self.maze[self.player_position[0]][self.player_position[1] + 1] == '#':
                    client.send(info_message_PERETE.encode("utf-8"))
                    moves += 1
                else:
                    client.send(info_message_LOSE.encode("utf-8"))
                    return
            else:
                client.send(info_message_WRONG_INPUT.encode("utf-8"))
            
            #updatarea pozitiei in labirint inainte sa fie printat in linia de comanda a serverului
            self.maze[self.player_position[0]][self.player_position[1]] = 'J'

            for row in self.maze:
                print(' '.join(row))
        
            

    #functia care porneste server-ul si il face sa asculte cererile clientului
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.server_port))
        server.listen()

        while True:
            client, addr = server.accept()

            print(f"Conexiune noua la adresa {addr}")

            begin_message = client.recv(1024).decode("utf-8")

            if begin_message == "START":
                while begin_message == "START":
                    moves = self.start_game(client, server)
                    if moves is not None:
                        info_message_WIN = f"Ai reușit! Ai ieșit din labirint în {moves} mișcări.\nTasteaza 'START' pentru a reincepe jocul sau 'STOP' pentru a inchide conexiunea!."
                        client.send(info_message_WIN.encode("utf-8"))
                    #generam pozitiile playerilor si labirintul inca o data
                    self.maze, self.exit_position = self.generate_maze()
                    self.player_position, self.monster_position = self.generate_players_position()
                    begin_message = client.recv(1024).decode("utf-8")
                    if begin_message == "STOP":
                        good_bye_message = "La revedere!"
                        client.send(good_bye_message.encode("utf-8"))
                        client.close()
            else:
                error_message = "Tasteaza 'START' pentru a incepe jocul sau 'STOP' pentru a inchide conexiunea!"
                client.send(error_message.encode("utf-8"))
            
    
if __name__ == '__main__':
    maze_server = Maze()
    maze_server.start()

