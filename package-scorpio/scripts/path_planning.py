#!/usr/bin/env python3
import rospy

if __name__ == '__main__':
    rospy.logerr("The main module is main.py!")

# funkcja dodajaca ruchy w przod lub w tyl w zaleznosci od polozenia celu
def append_moves(goal, current_position, moves):
    if current_position < goal:
        for i in range(goal-current_position):
            moves.append(2)
    else:
        for i in range(current_position-goal):
            moves.append(3)

# funkcja zwracajaca wszystkie komorki sasiednie wzgledem podanej w parametrze
def get_adj_cells(id):
    cells = []
    if id - 50 >= 0:        # poludnie
        cells.append(id-50)
    if id + 50 < 2500:      # polnoc
        cells.append(id+50)
    if (id-1)//50 == id//50:    # zachod
        cells.append(id-1)
    if (id+1)//50 == id//50:    # wschod
        cells.append(id+1)
    return cells

# funkcja do zbudowania sekwencji ruchow w oparciu o wynik algorytmu Dijkstry
def build_sequence(prevCell, prev, current_orientation):
    path = []
    while True: # zbudowanie w tablicy path[] sekwencji komorek tworzacych odnaleziona sciezke
        path.insert(0, prevCell)
        prevCell = prev[prevCell]
        if prevCell == -1:
            break
    moves = []
    for i in range(1, len(path)): # zbudowanie sekwencji ruchow w oparciu o tablice path[]
        # wewatrz tej petli dokladane sa kolejne ruchy do sekwencji
        # w polaczeniu z offsetem wybierany jest odpowiedni zestaw ruchow w zaleznosci od orientacji lazika
        offset = 0
        if path[i] == path[i-1] + 50:
            offset = 0
        elif path[i] == path[i-1] + 1:
            offset = 1
        elif path[i] == path[i-1] - 50:
            offset = 2
        elif path[i] == path[i-1] - 1:
            offset = 3
        else:
            rospy.logerr("Error while building a sequence of moves!")
            return []
        
        # switch do wyboru przejscia
        if (-current_orientation + offset) % 4 == 0: # na komorke z przodu
            moves.append(2)
        elif (-current_orientation + offset) % 4 == 1: # na komorke po prawej
            moves.extend([1,2])
            current_orientation = (current_orientation+1)%4 # korekta orientacji
        elif (-current_orientation + offset) % 4 == 2: # na komorke za lazikiem
            moves.extend([0,0,2])
            current_orientation = (current_orientation+2)%4 # korekta orientacji
        elif (-current_orientation + offset) % 4 == 3: # na komorke po lewej
            moves.extend([0,2])
            current_orientation = (current_orientation-1)%4 # korekta orientacji
        else:
            rospy.logerr("Error while building a sequence of moves!")
            return []
    return moves

# funkcja do odnalezienia optymalnej sciezki algorytmem Dijkstry,
# uwzgledniajaca ograniczenia podane w tresci zadania
def find_path_by_Dijkstra(goal_x, goal_y, current_x, current_y, mapData):
    if goal_x == current_x and goal_y == current_y: # edge case - cel jest taki sam jak pozycja startowa
        return []
    # inicjalizacja odpowiednich tablic
    dist = [2000000000] * 2500  # tablica do przechowania optymalnej dlugosci do danej komorki z komorki poczatkowej
    prev = [-1] * 2500          # tablica do zapamietania poprzedniej komorki wzgledem podanej w indeksie
    visited = [False] * 2500    # tablica do okreslenia ktore komorki byly juz przegladane celem unikniecia ponownego przegladu
    
    dist[current_x + current_y * 50] = 0 # komorka poczatkowa
    for i in range(2500):
        u = -1
        for i in range(2500):   # odnalezienie nie przegladanej komorki o najmniejszej wartosci dist[]
            if not visited[i] and (u == -1 or dist[i] < dist[u]):
                u = i
        if u == -1: # przerwanie petli jesli dalsza eksploracja jest niemozliwa z powodu przeszkod w terenie
            break
        visited[u] = True
        neighbors = get_adj_cells(u) # zebranie sasiednich komorek
        for v in neighbors:
            if not visited[v]:
                # krawedz jako roznica wysokosci pomiedzy komorkami
                # (faworyzowanie rowniny wzgledem gorzystego terenu w przypadku sciezki zlozonej z takiej samej liczby komorek)
                edge = abs(mapData[u] - mapData[v]) 
                if edge <= 10:
                    if dist[u] + edge < dist[v]:
                        dist[v] = dist[u] + edge
                        prev[v] = u
        if u == goal_x + goal_y * 50: # przerwanie petli jesli osiagnieto komorke docelowa
            break

    if prev[goal_x + goal_y * 50] == -1 and goal_x != current_x and goal_y != current_y:
        rospy.logerr("Destination unreachable! Choose another cell or generate map again!")
        return []
    return prev

def find_path(goal_x, goal_y, current_x, current_y, current_orientation, mapData):
    moves_sequence = []
    prev = find_path_by_Dijkstra(goal_x, goal_y, current_x, current_y, mapData)
    if prev:
        moves_sequence = build_sequence(goal_x + goal_y * 50, prev, current_orientation)
    return moves_sequence
