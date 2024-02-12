from enum import Enum
import tkinter as tk


class Player(Enum):
    X = "X"
    O = "O"
    DRAW = "Draw"


class Messages(Enum):
    WARNING_SPEECH = "Please specify the row and column by saying two numbers between one and the size of the chosen board type. For example, say 'first row and second column' to place your move in the first row and second column."
    WARNING_TEXT = "Please specify the row and column by stating two numbers between one and the size of the chosen board type. For instance, you can type 'first row and second column' to indicate the first row and second column. Alternatively, you can type '1 row and 2 column' or simply '1 2' separated with space."
    QUIT = "Do you want to quit the game? (y/n): "
    GAME_OVER = "{0}\nrematch?"
    Player_TURN = "Player {0}'s turn. Please make your move."
    INPUT_TYPE_ERROR = "input_type must be 1 for text input or 2 for speech input: {0} is not a valid input type."
    WINNER = "Player {0} wins :)"
    DRAW = "It's a draw :|"
    GOOGLE_UNKNOWN_ERROR = "Google Speech Recognition could not understand audio!"
    GOOGLE_REQUEST_ERROR = (
        "Could not request results from Google Speech Recognition service; {0}"
    )
    GOOGLE_SPEECH = "Google Speech Recognition thinks you said: {0}"


class BoardInputTypeDialog(tk.Toplevel):
    """
    A dialog box for choosing the board type and input type.

    Attributes:
        board_type: The chosen board type.
        input_type: The chosen input type.
    """

    def __init__(self, parent):
        """
        Initialize the dialog box.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self.title("Board type and Input type")
        self.geometry("320x150")  # Adjust the size to fit the new buttons
        self.resizable(False, False)
        self.board_type = tk.IntVar(master=parent)
        self.input_type = tk.IntVar(master=parent)
        self.board_type.set(0)
        self.input_type.set(0)
        self.confirm_button = tk.Button(
            self, text="Confirm", command=self.set_types, state="disabled"
        )
        self.confirm_button.grid(row=4, column=0, columnspan=3, pady=10)

        # Configure the grid to center the widgets
        for i in range(3):
            self.columnconfigure(i, weight=1)
        for i in range(5):
            self.rowconfigure(i, weight=1)
        tk.Label(self, text="Choose a board type:").grid(
            row=0, column=0, columnspan=3, sticky="nsew"
        )
        tk.Radiobutton(
            self,
            text="3x3",
            variable=self.board_type,
            value=3,
            command=self.check_selection,
        ).grid(row=1, column=0, padx=10, sticky="nsew")
        tk.Radiobutton(
            self,
            text="5x5",
            variable=self.board_type,
            value=5,
            command=self.check_selection,
        ).grid(row=1, column=1, padx=10, sticky="nsew")
        tk.Radiobutton(
            self,
            text="7x7",
            variable=self.board_type,
            value=7,
            command=self.check_selection,
        ).grid(row=1, column=2, padx=10, sticky="nsew")
        tk.Label(self, text="Choose an input type:").grid(
            row=2, column=0, columnspan=3, sticky="nsew"
        )
        tk.Radiobutton(
            self,
            text="Text",
            variable=self.input_type,
            value=1,
            command=self.check_selection,
        ).grid(row=3, column=0, padx=10, sticky="nsew")
        tk.Radiobutton(
            self,
            text="Speech",
            variable=self.input_type,
            value=2,
            command=self.check_selection,
        ).grid(row=3, column=1, padx=10, sticky="nsew")

    def check_selection(self):
        """
        Check if both options have been chosen and enable the "Confirm" button if they have.
        """
        if self.board_type.get() != 0 and self.input_type.get() != 0:
            self.confirm_button["state"] = "normal"

    def set_types(self):
        """
        Set the board type and input type and close the dialog box.
        """
        self.board_type = self.board_type.get()
        self.input_type = self.input_type.get()
        print("Board type:", f"{self.board_type}x{self.board_type}")
        print("Input type:", "Text" if self.input_type == 1 else "Speech")
        self.destroy()


class PlaceholderEntry(tk.Entry):
    """
    A text input widget with a placeholder.

    Attributes:
        placeholder: The placeholder text.
    """

    def __init__(self, parent=None, placeholder="", **kwargs):
        """
        Initialize the text input widget.

        Args:
            parent: The parent widget.
            placeholder: The placeholder text.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.insert(0, self.placeholder)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        """
        Remove the placeholder text when the widget is in focus.

        Args:
            event: The event object.
        """
        if self.get() == self.placeholder:
            self.delete(0, "end")

    def on_focus_out(self, event):
        """
        Insert the placeholder text when the widget is out of focus.

        Args:
            event: The event object.
        """
        if not self.get():
            self.insert(0, self.placeholder)

    def update(self, placeholder=""):
        """
        Update the placeholder.
        """
        self.delete(0, "end")
        self.insert(0, placeholder)
