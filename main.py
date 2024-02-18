import numpy as np
import tkinter as tk
from tkinter import messagebox
from util import BoardInputTypeDialog, Player, Messages, PlaceholderEntry
import speech_recognition as sr
# need for first time run
# import nltk
# nltk.download('punkt')
from nltk.tokenize import word_tokenize


class TicTacToe:
    ## Inits ##
    def __init__(self, title="Tic Tac Toe", rows=3, input_type=1):
        """
        Initializes the Tic Tac Toe game.

        Parameters:
        - title (str): The title of the game window.
        - rows (int): The number of rows and columns in the game board.
        - input_type (int): The input type. 1 for text, 2 for speech.
        """

        self.window = tk.Tk()
        self.window.title(f"{title} {rows}x{rows}")
        self.rows = rows
        self.board = np.zeros((self.rows, self.rows), dtype=int)
        self.input_type = input_type
        self.current_player = Player.X
        self.winner = None
        self.mic_is_on = False

    def init_input_type(self):
        """
        Initializes the input type.
        """
        # text input
        if self.input_type == 1:
            # turn of mic if it is on
            if self.mic_is_on:
                self.listening(wait_for_stop=False)
            if self.winner is None and self.window.winfo_exists():
                self.create_text_input(readonly=False)

        # speech input
        elif self.input_type == 2:
            self.mic_is_on = True
            # obtain audio from the microphone
            self.r = sr.Recognizer()
            self.m = sr.Microphone()
            # calibrate once
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
            # start listening
            self.listening = self.r.listen_in_background(self.m, self.process_speech)
            if self.winner is None and self.window.winfo_exists():
                self.create_text_input(readonly=True)
        else:
            raise ValueError(Messages.INPUT_TYPE_ERROR.value.format(self.input_type))

        print(Messages.Player_TURN.value.format(self.current_player.value))

    def init_board(self):
        """
        Creates the game board with buttons using tkinter.
        """
        for row in range(self.rows):
            for col in range(self.rows):
                self.create_button(row, col)

    ## Create ##
    def create_text_input(self, readonly):
        """
        Creates an entry field and a submit button for text input.
        """
        self.entry = PlaceholderEntry(
            self.window,
            placeholder=Messages.Player_TURN.value.format(self.current_player.value),
            readonly=readonly
        )
        self.entry.grid(
            row=self.rows + 1,
            column=0,
            columnspan=self.rows - 1,
            sticky="nsew",
        )
        if not readonly: 
            self.submit_button = tk.Button(
            self.window,
            text="Submit",
            command=self.process_text,
            activebackground="#0096c7",
            background="#00b4d8",
            cursor="hand2",
            font=("Times New Roman", 11, "bold"),
        )
            self.submit_button.grid(row=self.rows + 1, column=self.rows - 1, sticky="nsew")

    def create_button(self, row, col):
        """
        create the buttons for the game board.
        """

        button = tk.Button(
            self.window,
            text="",
            font=("Times New Roman", 50),
            height=2,
            width=6,
            bg="black",
            command=lambda row=row, col=col: self.handle_click(row, col),
        )
        button.grid(row=row, column=col, sticky="news")

        # buttons expand with window
        tk.Grid.rowconfigure(self.window, row, weight=1)
        tk.Grid.columnconfigure(self.window, col, weight=1)
    
    def recreate_board(self):
        """
        Resets the game board for a rematch.
        """
        board_type, input_type = msg_box()
        if (
            (board_type is None)
            | (board_type == 0)
            | (input_type is None)
            | (input_type == 0)
        ):
            return
        self.board = np.zeros((board_type, board_type), dtype=int)
        self.current_player = Player.X
        self.winner = None
        # same board
        if self.rows == board_type:
            for row in range(self.rows):
                for col in range(self.rows):
                    self.config_button(row, col)
        else:
            self.rows = board_type
            # remove all widgets
            for widget in self.window.winfo_children():
                widget.grid_forget()
            # create new board
            self.init_board()

        # different input type
        if self.input_type != input_type:
            self.input_type = input_type
            self.init_input_type()

    ## Config ##
    def config_button(self, row, col, text="", color="black", background="black"):
        """
        Configures a button on the game board.

        Parameters:
        - row (int): The row index of the button.
        - col (int): The column index of the button.
        - text (str): The text to display on the button. Default is an empty string.
        - color (str): The color of the text on the button. Default is "black".
        """
        button = self.window.grid_slaves(row=row, column=col)[0]
        button.config(text=text, fg=color, bg=background)

    def config_bground(self, coordinates):
        """
        Changes the background color of the buttons at the given coordinates.

        Parameters
        ----------
        coordinates : list of tuple
            A list of tuples where each tuple contains the row and column
            indices of a button.

        """
        for coord in coordinates:
            row, col = coord
            text = Player.X.value if self.board[row, col] == 1 else Player.O.value
            color = "red" if self.board[row, col] == 1 else "green"
            self.config_button(row, col, text=text, color=color, background="white")

    ## Handle ##
    def handle_click(self, row, col):
        """
        Handles a click event on a button at the given row and column.

        """
        if self.winner is None and self.board[row, col] == 0:
            self.board[row, col] = 1 if self.current_player == Player.X else 2
            color = "red" if self.current_player == Player.X else "green"
            self.config_button(row, col, text=self.current_player.value, color=color)
            self.current_player = (
                Player.O if self.current_player == Player.X else Player.X
            )
            self.check_winner()
        # update the entry field
        self.entry.update(Messages.Player_TURN.value.format(self.current_player.value))
        print(Messages.Player_TURN.value.format(self.current_player.value))

    ## Check ##
    def check_winner(self):
        """
        Checks for a winner or a tie in the game.
        """
        # Check rows
        for i, row in enumerate(self.board):
            winner, coordinates = self.check_consecutive(
                [(cell, (i, j)) for j, cell in enumerate(row)]
            )
            if winner:
                self.config_bground(coordinates)
                break

        # Check columns
        for j in range(self.rows):
            column = [(self.board[i][j], (i, j)) for i in range(self.rows)]
            winner, coordinates = self.check_consecutive(column)
            if winner:
                self.config_bground(coordinates)
                break

        # Check diagonals
        if self.rows == 3:
            self.check_3x3_diagonals()
        elif self.rows == 5:
            self.check_5x5_diagonals()
        else:
            self.check_7x7_diagonals()

        # check for a draw
        if np.all(self.board) and self.winner is None:
            self.winner = Player.DRAW.value

        # declare winner
        if self.winner:
            if self.winner == Player.DRAW.value:
                message = Messages.DRAW.value
            else:
                message = Messages.WINNER.value.format(self.winner)

            play_again = messagebox.askyesno(
                "Game Over", Messages.REMATCH.value.format(message)
            )

            # recreate board if answer is yes otherwise close the window
            if play_again:
                self.recreate_board()
            else:
                # stop listening before closing the window
                if self.mic_is_on:
                    self.listening(wait_for_stop=False)
                self.window.quit()
                return

    def check_3x3_diagonals(self):
        """
        Checks for three consecutive X or O in diagonals for a 3x3 board.

        Diagonals include the main diagonal and anti-diagonal.

        """
        diagonals = [
            [(self.board[i][i], (i, i)) for i in range(3)],  # main diagonal
            [(self.board[i][2 - i], (i, 2 - i)) for i in range(3)],  # anti-diagonal
        ]

        for diagonal in diagonals:
            winner, coordinates = self.check_consecutive(diagonal)
            if winner:
                self.config_bground(coordinates)
                return True, coordinates

        return False, []

    def check_5x5_diagonals(self):
        """
        Checks for four consecutive X or O in diagonals for a 5x5 board.

        Diagonals include the main diagonal and anti-diagonal.

        """
        diagonals = [
            [(self.board[i][i], (i, i)) for i in range(5)],  # main diagonal
            [(self.board[i][4 - i], (i, 4 - i)) for i in range(5)],  # anti-diagonal
        ]

        for i in range(1, 2):
            # main diagonal shifted right
            diagonals.append([(self.board[j][j + i], (j, j + i)) for j in range(5 - i)])
            # main diagonal shifted left
            diagonals.append([(self.board[j + i][j], (j + i, j)) for j in range(5 - i)])
            # anti-diagonal shifted right
            diagonals.append(
                [(self.board[j][4 - (j + i)], (j, 4 - (j + i))) for j in range(5 - i)]
            )
            # anti-diagonal shifted left
            diagonals.append(
                [(self.board[j + i][4 - j], (j + i, 4 - j)) for j in range(5 - i)]
            )

        for diagonal in diagonals:
            winner, coordinates = self.check_consecutive(diagonal)
            if winner:
                self.config_bground(coordinates)
                return True, coordinates

        return False, []

    def check_7x7_diagonals(self):
        """
        Checks for four consecutive X or O in diagonals for a 7x7 board.

        Diagonals include the main diagonal and anti-diagonal.

        """
        diagonals = [
            [(self.board[i][i], (i, i)) for i in range(7)],  # main diagonal
            [(self.board[i][6 - i], (i, 6 - i)) for i in range(7)],  # anti-diagonal
        ]

        # Add shifted diagonals
        for i in range(1, 4):
            # main diagonal shifted right
            diagonals.append([(self.board[j][j + i], (j, j + i)) for j in range(7 - i)])
            # main diagonal shifted left
            diagonals.append([(self.board[j + i][j], (j + i, j)) for j in range(7 - i)])
            # anti-diagonal shifted right
            diagonals.append(
                [(self.board[j][6 - (j + i)], (j, 6 - (j + i))) for j in range(7 - i)]
            )
            # anti-diagonal shifted left
            diagonals.append(
                [(self.board[j + i][6 - j], (j + i, 6 - j)) for j in range(7 - i)]
            )

        for diagonal in diagonals:
            winner, coordinates = self.check_consecutive(diagonal)
            if winner:
                self.config_bground(coordinates)
                return True

        return False

    def check_consecutive(self, line):
        """
        Checks if there are four consecutive X or O in the given line.

        Parameters:
        - line (list): The row, column, or diagonal to check.

        Returns:
        - bool: True if there are four consecutive X or O, False otherwise.
        """
        consecutive_count = 0
        last_cell = None
        consecutive_to_win = 4 if self.rows == 5 or self.rows == 7 else 3
        coordinates = []
        for i, (cell, coord) in enumerate(line):
            if cell == 0:
                consecutive_count = 0
                last_cell = None
            elif cell == last_cell:
                consecutive_count += 1
                coordinates.append(coord)
                if consecutive_count == consecutive_to_win:
                    self.winner = Player.X.value if last_cell == 1 else Player.O.value
                    return True, coordinates
            else:
                consecutive_count = 1
                last_cell = cell
                coordinates = [coord]

        return False, []
    
    ## Process ##
    def process_text(self):
        """
        Processes the text input.
        """
        move = self.entry.get()
        self.entry.update()
        try:
            row, col = self.extract_coordinates(move)
            if (row is not None) and (col is not None):
                self.handle_click(row, col)
            else:
                raise ValueError
        except ValueError:
            print("Invalid move!", Messages.WARNING_TEXT.value)

    def process_speech(self, recognizer, audio):
        """
        This function is called when audio is received from the microphone.

        Parameters:
        - recognizer (Recognizer): The speech recognizer.
        - audio (AudioData): The audio data.
        """
        try:
            speech = recognizer.recognize_google(audio)
            print(Messages.GOOGLE_SPEECH.value.format(speech))
            row, col = self.extract_coordinates(speech)
            if (row is not None) and (col is not None):
                self.window.after(0, self.handle_click, row, col)
            else:
                raise ValueError
        except sr.UnknownValueError:
            print(Messages.GOOGLE_UNKNOWN_ERROR.value)
        except sr.RequestError as e:
            print(Messages.GOOGLE_REQUEST_ERROR.value.format(e))
        except ValueError:
            print("Invalid move!", Messages.WARNING_SPEECH.value)

    def extract_coordinates(self, input):
        """
        Extracts the row and column indices from the input.

        Parameters:
        - input (str): The input string.

        Returns:
        - tuple: The row and column indices.
        """
        # Map spoken/written numbers
        number_map = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2}
        if self.rows == 5:
            number_map.update({"fourth": 3, "4th": 3})
            number_map.update({"fifth": 4, "5th": 4})
        elif self == 7:
            number_map.update({"sixth": 5, "6th": 5})
            number_map.update({"seventh": 6, "7th": 6})

        # tokenize the speech/text
        tokens = word_tokenize(input)
        row = None
        col = None
        for i, token in enumerate(tokens):
            if token in number_map:
                if i + 1 < len(tokens):
                    if tokens[i + 1] == "row" or tokens[i + 1] == "rows":
                        row = number_map[token]
                    elif tokens[i + 1] == "column" or tokens[i + 1] == "columns" or tokens[i + 1] == "col" or tokens[i + 1] == "cols":
                        col = number_map[token]
                    else:
                        raise ValueError
            elif token == "middle":
                row = col = self.rows // 2
            else:
                try:
                    num = int(token)
                    if (num >= 1) and (num <= self.rows):
                        if row is None:
                            row = num - 1
                        elif col is None:
                            col = num - 1
                        else:
                            raise ValueError
                except ValueError:
                    continue
        return row, col
    ## Main ##
    def main_loop(self):
        """
        Starts the main event loop to keep the game window alive.
        """
        self.window.protocol("WM_DELETE_WINDOW", self.close_main_app)
        self.window.bind("<Destroy>", self.close_main_app)
        self.window.mainloop()

    def close_main_app(self):
        """
        Closes the game window.
        """
        self.window.quit()


def msg_box():
    """
    start message box to determinate board type
    """
    msg_window = tk.Tk()
    msg_window.withdraw()
    dialog = BoardInputTypeDialog(msg_window)
    msg_window.wait_window(dialog)
    return dialog.board_type, dialog.input_type


def start_game():
    """
    Start the game of Tic Tac Toe.

    This function first opens a dialog box to ask the user to choose the board type.
    If the user closes the dialog box without choosing a board type, the function returns and the game does not start.
    If the user chooses a board type, a new game of Tic Tac Toe is started with a board of the chosen type.
    """
    try:
        board_type, input_type = msg_box()
        if (
            (board_type is None)
            or (board_type == 0)
            or (type(board_type) is not int)
            or (input_type is None)
            or (input_type == 0)
            or (type(input_type) is not int)
        ):
            return
        game = TicTacToe(rows=board_type, input_type=input_type)
        game.init_board()
        game.init_input_type()
        while True:
            try:
                game.main_loop()
                if game.mic_is_on:
                        game.listening(wait_for_stop=False)
                return
            except KeyboardInterrupt:
                print(Messages.QUIT.value)
                cm_input = input()
                if cm_input.lower() in ["y", "yes"]:
                    if game.mic_is_on:
                        game.listening(wait_for_stop=False)
                    print("Quiting...")
                    break
    except Exception as e:
        # stop listening
        if game.mic_is_on:
            game.listening(wait_for_stop=False)
        print(e)
        print(Messages.GAME_OVER.value)
        return

if __name__ == "__main__":
    start_game()
