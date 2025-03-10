
import random
import os
import time

class Ship:
    
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.positions = [] 
        self.hits = [] 
    
    def is_placed(self):
        return len(self.positions) > 0
    
    def place(self, positions):
        
        if len(positions) != self.size:
            raise ValueError(f"Le nombre de positions ({len(positions)}) ne correspond pas à la taille du navire ({self.size})")
        self.positions = positions
    
    def is_hit(self, position):
       
        if position in self.positions:
            self.hits.append(position)
            return True
        return False
    
    def is_sunk(self):
        return len(self.hits) == self.size


class Board:
    
    def __init__(self, size=10):
        self.size = size
        self.grid = [['~' for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.shots = []  
    
    def add_ship(self, ship):

        self.ships.append(ship)
        for x, y in ship.positions:
            self.grid[y][x] = 'O'
    
    def can_place_ship(self, positions):
        for x, y in positions:
            if x < 0 or x >= self.size or y < 0 or y >= self.size:
                return False
        
      
        for x, y in positions:
            if self.grid[y][x] != '~':
                return False
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in positions:
                        if self.grid[ny][nx] == 'O':
                            return False
        
        return True
    
    def place_ship_randomly(self, ship):
        max_attempts = 100
        for _ in range(max_attempts):
            orientation = random.randint(0, 1)
            
            if orientation == 0:  
                x = random.randint(0, self.size - ship.size)
                y = random.randint(0, self.size - 1)
                positions = [(x + i, y) for i in range(ship.size)]
            else:  
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - ship.size)
                positions = [(x, y + i) for i in range(ship.size)]
            
            if self.can_place_ship(positions):
                ship.place(positions)
                self.add_ship(ship)
                return True
        
        return False
    
    def place_all_ships_randomly(self, ships):

        for ship in ships:
            if not self.place_ship_randomly(ship):
                return False
        return True
    
    def shoot(self, position):
   
        x, y = position
        
      
        if position in self.shots:
            return None, None
        
        self.shots.append(position)
        

        hit = False
        ship_sunk = None
        
        for ship in self.ships:
            if ship.is_hit(position):
                hit = True
                self.grid[y][x] = 'X'
                if ship.is_sunk():
                    ship_sunk = ship
                break
        
        if not hit:
            self.grid[y][x] = '-'
        
        return hit, ship_sunk
    
    def all_ships_sunk(self):

        return all(ship.is_sunk() for ship in self.ships)
    
    def display(self, hide_ships=False):

        display_grid = [row[:] for row in self.grid]

        if hide_ships:
            for y in range(self.size):
                for x in range(self.size):
                    if display_grid[y][x] == 'O':
                        display_grid[y][x] = '~'
        
        header = '   ' + ' '.join(chr(65 + i) for i in range(self.size))

        rows = [header]
        for i, row in enumerate(display_grid):
            row_str = f'{i+1:2d} ' + ' '.join(row)
            rows.append(row_str)
        
        return '\n'.join(rows)


class Player:

    
    def __init__(self, name, is_computer=False):

        self.name = name
        self.is_computer = is_computer
        self.board = Board()
        self.opponent_board = Board() 
    def setup_ships(self):
       
        ships = [
            Ship("Porte-avions", 5),
            Ship("Cuirassé", 4),
            Ship("Croiseur", 3),
            Ship("Sous-marin", 3),
            Ship("Destroyer", 2)
        ]
        
        if self.is_computer:
            self.board.place_all_ships_randomly(ships)
        else:
            self._manual_ship_placement(ships)
    
    def _manual_ship_placement(self, ships):
      
        for ship in ships:
            placed = False
            while not placed:
                clear_screen()
                print(f"Placement des navires - {self.name}")
                print(self.board.display())
                print(f"\nPlacez votre {ship.name} ({ship.size} cases)")
                
                try:
                    position_input = input("Position (ex: A1): ").strip().upper()
                    if len(position_input) < 2:
                        print("Format invalide. Exemple: A1")
                        time.sleep(1)
                        continue
                    
                    col = ord(position_input[0]) - ord('A')
                    row = int(position_input[1:]) - 1
                    
                    orientation_input = input("Orientation (H: horizontal, V: vertical): ").strip().upper()
                    if orientation_input not in ['H', 'V']:
                        print("Orientation invalide. Utilisez H ou V.")
                        time.sleep(1)
                        continue
                    
                    if orientation_input == 'H':
                        positions = [(col + i, row) for i in range(ship.size)]
                    else:  # 'V'
                        positions = [(col, row + i) for i in range(ship.size)]
                    
                    if self.board.can_place_ship(positions):
                        ship.place(positions)
                        self.board.add_ship(ship)
                        placed = True
                    else:
                        print("Impossible de placer le navire à cette position.")
                        time.sleep(1)
                
                except (ValueError, IndexError):
                    print("Position invalide. Exemple: A1")
                    time.sleep(1)
    
    def get_shot(self):

        if self.is_computer:
            return self._get_computer_shot()
        else:
            return self._get_human_shot()
    
    def _get_human_shot(self):

        while True:
            try:
                position_input = input("Position du tir (ex: A1): ").strip().upper()
                if len(position_input) < 2:
                    print("Format invalide. Exemple: A1")
                    continue
                
                col = ord(position_input[0]) - ord('A')
                row = int(position_input[1:]) - 1
                
                if 0 <= col < self.opponent_board.size and 0 <= row < self.opponent_board.size:
                    position = (col, row)
                    if position in self.opponent_board.shots:
                        print("Vous avez déjà tiré à cette position.")
                        continue
                    return position
                else:
                    print(f"Position hors limites. Utilisez A-J et 1-10.")
            
            except (ValueError, IndexError):
                print("Position invalide. Exemple: A1")
    
    def _get_computer_shot(self):

        available_positions = []
        for x in range(self.opponent_board.size):
            for y in range(self.opponent_board.size):
                position = (x, y)
                if position not in self.opponent_board.shots:
                    available_positions.append(position)
        
        return random.choice(available_positions)
    
    def receive_shot_result(self, position, hit, ship_sunk):

        x, y = position
        self.opponent_board.shots.append(position)
        
        if hit:
            self.opponent_board.grid[y][x] = 'X'
        else:
            self.opponent_board.grid[y][x] = '-'


class Game:
 
    def __init__(self):
        self.human_player = Player("Joueur")
        self.computer_player = Player("Ordinateur", is_computer=True)
        self.current_player = self.human_player
    
    def setup(self):
    
        print("=== BATAILLE NAVALE ===\n")
        print("Bienvenue dans le jeu de bataille navale!")
        print("Vous allez affronter l'ordinateur.")
        print("Placez vos navires sur la grille.\n")
        
        input("Appuyez sur Entrée pour commencer...")
        
        self.human_player.setup_ships()
        self.computer_player.setup_ships()
        
        self.human_player.opponent_board = Board()
        self.computer_player.opponent_board = Board()
    
    def play(self):
        """Joue la partie."""
        self.setup()
        
        game_over = False
        while not game_over:
            self._play_turn()
            
            if self.computer_player.board.all_ships_sunk():
                self._display_game_state()
                print("\n🎉 Félicitations! Vous avez gagné! 🎉")
                game_over = True
            elif self.human_player.board.all_ships_sunk():
                self._display_game_state()
                print("\n😢 L'ordinateur a gagné. 😢")
                game_over = True
            
            if self.current_player == self.human_player:
                self.current_player = self.computer_player
            else:
                self.current_player = self.human_player
        
        print("\nFin de la partie.")
    
    def _play_turn(self):
        if self.current_player == self.human_player:
            self._human_turn()
        else:
            self._computer_turn()
    
    def _human_turn(self):
        self._display_game_state()
        
        print(f"\nC'est à votre tour de jouer.")
        position = self.human_player.get_shot()
        
        hit, ship_sunk = self.computer_player.board.shoot(position)
        self.human_player.receive_shot_result(position, hit, ship_sunk)
        
        x, y = position
        position_str = f"{chr(65 + x)}{y + 1}"
        
        if hit:
            print(f"\nTouché en {position_str}!")
            if ship_sunk:
                print(f"Vous avez coulé le {ship_sunk.name} de l'ordinateur!")
        else:
            print(f"\nÀ l'eau en {position_str}.")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def _computer_turn(self):
        print("\nC'est au tour de l'ordinateur...")
        time.sleep(1)
        
        position = self.computer_player.get_shot()
        
        hit, ship_sunk = self.human_player.board.shoot(position)
        self.computer_player.receive_shot_result(position, hit, ship_sunk)
        
        x, y = position
        position_str = f"{chr(65 + x)}{y + 1}"
        
        if hit:
            print(f"L'ordinateur a touché en {position_str}!")
            if ship_sunk:
                print(f"L'ordinateur a coulé votre {ship_sunk.name}!")
        else:
            print(f"L'ordinateur a tiré à l'eau en {position_str}.")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def _display_game_state(self):
        """Affiche l'état du jeu."""
        clear_screen()
        
        print("=== BATAILLE NAVALE ===\n")
        
        print("Grille de l'ordinateur:")
        print(self.computer_player.board.display(hide_ships=True))
        
        print("\nVotre grille:")
        print(self.human_player.board.display())
        
        human_ships_remaining = sum(1 for ship in self.human_player.board.ships if not ship.is_sunk())
        computer_ships_remaining = sum(1 for ship in self.computer_player.board.ships if not ship.is_sunk())
        
        print(f"\nNavires restants - Vous: {human_ships_remaining}, Ordinateur: {computer_ships_remaining}")


def clear_screen():
    """Efface l'écran de la console."""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    game = Game()
    game.play()
