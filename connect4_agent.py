import tkinter as tk
import random
import time

# Define the winning_score globally
winning_score = 1000000

class Connect4Game:
    def __init__(self):
        self.board = [[' ' for _ in range(7)] for _ in range(6)]  # Initialize empty board
        self.current_player = 'You'  # Human player starts first

    def is_valid_move(self, col):
        return self.board[0][col] == ' '

    def make_move(self, col):
        if self.is_valid_move(col):
            row = self.find_empty_row_in_col(col)
            if row is not None:
                self.board[row][col] = self.current_player
                return True
        return False

    def toggle_player(self):
        self.current_player = 'Opponent(AI)' if self.current_player == 'You' else 'You'

    def find_empty_row_in_col(self, col):
        for row in range(5, -1, -1):
            if self.board[row][col] == ' ':
                return row
        return None

    def check_winner(self):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1),(0,-1)]  # right, down, down-right, down-left,left
        for r in range(6):
            for c in range(7):
                if self.board[r][c] != ' ':
                    for dr, dc in directions:
                        if all(0 <= r + i * dr < 6 and 0 <= c + i * dc < 7 and self.board[r + i * dr][c + i * dc] == self.board[r][c] for i in range(4)):
                            return self.board[r][c]
        return None

    def check_draw(self):
        return all(self.board[0][col] != ' ' for col in range(7))

def evaluate(board, player):
    score = 0
    opponent = 'Opponent(AI)' if player == 'You' else 'You'
    directions = [(0, 1), (1, 0), (1, 1), (1, -1), (0, -1)]
    for r in range(6):
        for c in range(7):
            if board[r][c] == player or board[r][c] == opponent:
                current_player = board[r][c]
                for dr, dc in directions:
                    sequence_length = 0
                    for i in range(4):
                        nr, nc = r + i * dr, c + i * dc
                        if 0 <= nr < 6 and 0 <= nc < 7 and board[nr][nc] == current_player:
                            sequence_length += 1
                        else:
                            break
                    if sequence_length == 4:
                        score += winning_score if current_player == player else -winning_score
                    else:
                        score += 10 ** sequence_length if current_player == player else -10 ** sequence_length
    return score

def minimax(board, depth, alpha, beta, maximizing_player, game):
    current_winner = game.check_winner()
    if depth == 0 or current_winner or game.check_draw():
        if current_winner:
            return (winning_score if current_winner == game.current_player else -winning_score)
        else:
            return evaluate(board, game.current_player)

    if maximizing_player:
        max_eval = float('-inf')
        for col in range(7):
            if game.is_valid_move(col):
                row = game.find_empty_row_in_col(col)
                game.board[row][col] = game.current_player
                game.toggle_player()
                eval = minimax(game.board, depth - 1, alpha, beta, False, game)
                game.board[row][col] = ' '
                game.toggle_player()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for col in range(7):
            if game.is_valid_move(col):
                row = game.find_empty_row_in_col(col)
                game.board[row][col] = game.current_player
                game.toggle_player()
                eval = minimax(game.board, depth - 1, alpha, beta, True, game)
                game.board[row][col] = ' '
                game.toggle_player()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

class Connect4GUI:
    game_count = 1  # Class variable to track game count

    def __init__(self, master):
        self.master = master
        self.master.title("Connect Four")
        self.canvas = tk.Canvas(self.master, width=560, height=480, bg="white")
        self.canvas.pack()
        self.game = Connect4Game()
        self.draw_board()
        self.restart_button()
        self.current_winner_text = None

    def draw_board(self):
        for row in range(6):
            for col in range(7):
                x0, y0 = col * 80 + 2, row * 80 + 2
                x1, y1 = x0 + 76, y0 + 76
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
                if row == 5:
                    self.canvas.create_line(x0, y1, x1, y1, fill="black")
            if col == 6:
                self.canvas.create_line(x1, y0, x1, y1, fill="black")

    def restart_button(self):
        restart_button = tk.Button(self.master, text="↺", command=self.restart_game)
        restart_button.pack()

    def restart_game(self):
        self.canvas.delete("piece")
        self.game = Connect4Game()
        self.draw_board()
        if self.current_winner_text:
            self.canvas.delete(self.current_winner_text)
            self.current_winner_text = None
        Connect4GUI.game_count += 1  # Increment game count
        if Connect4GUI.game_count % 2 == 0:  # Check if it's Opponent(AI)'s turn to start
            self.game.current_player = 'Opponent(AI)'  # Set current player to Opponent(AI)
            self.master.after(500, self.ai_move)  # If AI starts, make its move after a delay

    def handle_click(self, event):
        col = (event.x - 2) // 80
        if self.game.make_move(col):
            self.draw_pieces()
            winner = self.game.check_winner()
            if winner:
                self.show_winner(winner)
            elif self.game.check_draw():
                self.show_draw()
            else:
                self.game.toggle_player()
                self.master.after(500, self.ai_move)  # Delay for AI move

    def draw_pieces(self):
        for row in range(6):
            for col in range(7):
                if self.game.board[row][col] != ' ':
                    color = "yellow" if self.game.board[row][col] == 'You' else "red"
                    x, y = col * 80 + 40, row * 80 + 40
                    self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=color, outline="black", tags="piece")

    def ai_move(self):
        # Check for winning move first
        for col in range(7):
            if self.game.is_valid_move(col):
                row = self.game.find_empty_row_in_col(col)
                self.game.board[row][col] = 'Opponent(AI)'
                if self.game.check_winner() == 'Opponent(AI)':  # AI wins by making this move
                    self.draw_pieces()
                    self.show_winner('Opponent(AI)')
                    return
                self.game.board[row][col] = ' '  # Undo the move

        # If no winning move, check for opponent's winning move to block
        for col in range(7):
            if self.game.is_valid_move(col):
                row = self.game.find_empty_row_in_col(col)
                self.game.board[row][col] = 'You'
                if self.game.check_winner() == 'You':  # Opponent wins if AI doesn't block
                    self.game.board[row][col] = ' '  # Undo the move
                    self.game.board[row][col] = 'Opponent(AI)'  # Block opponent's winning move
                    self.draw_pieces()
                    self.game.toggle_player()  # Correctly toggle back to human player
                    return
                self.game.board[row][col] = ' '  # Undo the move

        # If no winning or blocking move, use minimax with alpha-beta pruning
        best_score = float('-inf')
        best_col = None
        for col in range(7):
            if self.game.is_valid_move(col):
                row = self.game.find_empty_row_in_col(col)
                self.game.board[row][col] = 'Opponent(AI)'
                score = minimax(self.game.board, 4, float('-inf'), float('inf'), False, self.game)
                self.game.board[row][col] = ' '
                if score > best_score:
                    best_score = score
                    best_col = col

        # Make the best move found by minimax
        if best_col is not None:
            self.game.make_move(best_col)
            self.draw_pieces()
            winner = self.game.check_winner()
            if winner:
                self.show_winner(winner)
            elif self.game.check_draw():
                self.show_draw()
            else:
                self.game.toggle_player()

    def show_winner(self, winner):
        self.current_winner_text = self.canvas.create_text(280, 240, text=f"{winner} won!", font=("Arial", 24))

    def show_draw(self):
        self.current_winner_text = self.canvas.create_text(280, 240, text="It's a draw!", font=("Arial", 24))

def main():
    root = tk.Tk()
    gui = Connect4GUI(root)
    gui.canvas.bind("<Button-1>", gui.handle_click)
    root.mainloop()

if __name__ == "__main__":
    main()
