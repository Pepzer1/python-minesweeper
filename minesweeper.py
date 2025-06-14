import customtkinter as ctk
import json
import random as ra


class Config:
    """Handles configuration loading, saving, and theme management for the Minesweeper game."""

    def __init__(self):
        self._config_data = self.load_config()

    def load_config(self):
        """
        Load configuration from config.json file or create default config if file doesn't exist.

        Returns:
            dict: Configuration data containing themes, difficulties, and settings
        """
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default configuration if file is missing or corrupted
            default_config = {
                "current_diff": "easy",
                "current_theme": "dark",
                "initial_width": 500,
                "initial_height": 650,
                "best_time": {"easy": 9999, "normal": 9999, "hard": 9999},
                "difficulties": {
                    "easy": {"width": 9, "height": 9, "mines": 10},
                    "normal": {"width": 16, "height": 16, "mines": 40},
                    "hard": {"width": 30, "height": 16, "mines": 80},
                    "custom": {"width": 10, "height": 10, "mines": 1},
                },
                "themes": {
                    "light": {
                        "main_label": "#0D47A1",
                        "main_color": "#F5F5F5",
                        "hover_color": "#D0E8FF",
                        "accent_color": "#2196F3",
                        "text_color": "#212121",
                        "button_color": "#E0E0E0",
                        "pressed_color": "#B3E5FC",
                        "flag_color": "#FF7043",
                        "mines_color": "#E53935",
                        "start_color_fg": "#64B5F6",
                        "start_color_text": "#FFFFFF",
                        "start_color_hover": "#42A5F5",
                        "settings_color_fg": "#FFD54F",
                        "settings_color_text": "#000000",
                        "settings_color_hover": "#FFCA28",
                        "exit_color_mainmenu": "#EF5350",
                        "exit_color_text": "#FFFFFF",
                        "exit_color_hover": "#D32F2F",
                        "config_buttons_color": "#E1F5FE",
                        "config_buttons_hover": "#B3E5FC",
                        "config_buttons_text": "#000000",
                        "num_colors": {
                            "1": "#1976D2",
                            "2": "#388E3C",
                            "3": "#F57C00",
                            "4": "#7B1FA2",
                            "5": "#C2185B",
                            "6": "#0097A7",
                            "7": "#5D4037",
                            "8": "#455A64",
                        },
                    },
                    "dark": {
                        "main_label": "#64B5F6",
                        "main_color": "#1E1E1E",
                        "hover_color": "#2A2A2A",
                        "accent_color": "#64B5F6",
                        "text_color": "#E0E0E0",
                        "button_color": "#2C2C2C",
                        "pressed_color": "#424242",
                        "flag_color": "#FF7043",
                        "mines_color": "#EF5350",
                        "start_color_fg": "#64B5F6",
                        "start_color_text": "#FFFFFF",
                        "start_color_hover": "#42A5F5",
                        "settings_color_fg": "#26A69A",
                        "settings_color_text": "#FFFFFF",
                        "settings_color_hover": "#00796B",
                        "exit_color_mainmenu": "#E53935",
                        "exit_color_text": "#FFFFFF",
                        "exit_color_hover": "#B71C1C",
                        "config_buttons_color": "#37474F",
                        "config_buttons_hover": "#455A64",
                        "config_buttons_text": "#FFFFFF",
                        "num_colors": {
                            "1": "#64B5F6",
                            "2": "#81C784",
                            "3": "#FFB74D",
                            "4": "#BA68C8",
                            "5": "#F06292",
                            "6": "#4DD0E1",
                            "7": "#BCAAA4",
                            "8": "#90A4AE",
                        },
                    },
                },
            }
            # Save default configuration to file
            with open("config.json", "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def reload_config(self):
        """Reload configuration from file to reflect any external changes."""
        self._config_data = self.load_config()

    def theme(self, key):
        """
        Get theme color value by key for current theme.

        Args:
            key (str): Theme color key to retrieve

        Returns:
            str: Color value for the specified key
        """
        return self._config_data["themes"][self.current_theme].get(key)

    @property
    def config(self):
        """Get the complete configuration data."""
        return self._config_data

    @property
    def current_theme(self):
        """Get the currently selected theme name."""
        return self._config_data["current_theme"]

    @property
    def current_diff(self):
        """Get the currently selected difficulty level."""
        return self._config_data["current_diff"]

    @property
    def initial_width(self):
        """Get the initial window width."""
        return self._config_data["initial_width"]

    @property
    def initial_height(self):
        """Get the initial window height."""
        return self._config_data["initial_height"]

    @property
    def width(self):
        """Get the game field width for current difficulty."""
        return self._config_data["difficulties"][self.current_diff]["width"]

    @property
    def height(self):
        """Get the game field height for current difficulty."""
        return self._config_data["difficulties"][self.current_diff]["height"]

    @property
    def bombs(self):
        """Get the number of mines for current difficulty."""
        return self._config_data["difficulties"][self.current_diff]["mines"]

    @property
    def best_time(self):
        """Get the best time record for current difficulty."""
        return self._config_data["best_time"][self.current_diff]


class GameState:
    """Manages the current state of the Minesweeper game including field, mines, and timing."""

    def __init__(self, parent, config):
        self.app = parent
        self.config = config
        self.reset_game()

    def reset_game(self):
        """Reset all game state variables to initial values for a new game."""
        self.first_click = True
        self.running = False
        self.time_elapsed = 0
        self.def_zone = []  # Safe zone around first click
        self.field = []  # 2D array of Cell objects
        self.buttons = []  # 2D array of GUI buttons
        self.all_cords = []  # Coordinates of all non-mine cells
        self.danger_cords = []  # Available coordinates for mine placement
        self.mines = self.config.bombs

    def do_field(self, buttons, field_frame):
        """
        Initialize the game field with Cell objects.

        Args:
            buttons (list): 2D array of GUI buttons
            field_frame: Parent frame containing the field
        """
        self.buttons = buttons
        self.field = [
            [
                Cell(self, col, row, self.config, self.app, field_frame)
                for col in range(self.config.width)
            ]
            for row in range(self.config.height)
        ]

    def safe_zone(self, row, col):
        """
        Define safe zone around first click to prevent immediate mine hits.

        Args:
            row (int): Row coordinate of first click
            col (int): Column coordinate of first click
        """
        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                new_r = row + dr
                new_c = col + dc
                if 0 <= new_c < self.config.width and 0 <= new_r < self.config.height:
                    self.def_zone.append(new_r * self.config.width + new_c)

    def place_bombs(self):
        """
        Randomly place mines on the field, avoiding the safe zone.
        Uses linear coordinates for efficient placement.
        """
        bombs = self.config.bombs
        self.all_cords = [i for i in range(self.config.height * self.config.width)]
        # Remove safe zone from available mine placement coordinates
        self.danger_cords = list(set(self.all_cords) - set(self.def_zone))
        # Randomly select mine positions
        bomb_coords = ra.sample(self.danger_cords, bombs)
        self.all_cords = list(set(self.all_cords) - set(bomb_coords))
        # Convert linear coordinates to 2D coordinates
        unique_cords = [
            (cell // self.config.width, cell % self.config.width)
            for cell in bomb_coords
        ]
        # Place mines on the field
        for r, c in unique_cords:
            self.field[r][c].bomb = True

    def calculate_neighbor_bombs(self):
        """Calculate the number of adjacent mines for each non-mine cell."""
        for row in range(self.config.height):
            for col in range(self.config.width):
                if not self.field[row][col].bomb:
                    count = 0
                    # Check all 8 adjacent cells
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = row + dr, col + dc
                            # Verify coordinates are within bounds and cell contains mine
                            if (
                                0 <= nr < self.config.height
                                and 0 <= nc < self.config.width
                                and self.field[nr][nc].bomb
                            ):
                                count += 1
                    self.field[row][col].neighbor_bombs = count

    def update_timer(self):
        """
        Update game timer if game is running.

        Returns:
            int or None: Current elapsed time if running, None otherwise
        """
        if self.running:
            self.time_elapsed += 1
            return self.time_elapsed
        return None

    def check_best(self):
        """Check if current time is a new best record and save it if so."""
        if (
            self.config.current_diff != "custom"
            and self.time_elapsed < self.config.best_time
        ):
            # Update best time in configuration
            self.config.config["best_time"][
                self.config.current_diff
            ] = self.time_elapsed
            # Save updated configuration to file
            with open("config.json", "w") as f:
                json.dump(self.config.config, f, indent=2)


class MinesweeperApp(ctk.CTk):
    """Main application window for the Minesweeper game."""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.title("Minesweeper")

        # Set initial window size and layout
        self.geometry(f"{self.config.initial_width}x{self.config.initial_height}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize game state and build UI
        self.game_state = GameState(self, self.config)
        self.build_ui()

    def build_ui(self):
        """Build the main user interface starting with the greeting screen."""
        self.config.reload_config()
        self.geometry(f"{self.config.initial_width}x{self.config.initial_height}")
        greet_frame = GreetScreen(self, self.config, self.game_state)
        greet_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


class GreetScreen(ctk.CTkFrame):
    """Main menu screen with game start, settings, and exit options."""

    def __init__(self, parent, config, game_state):
        self.config = config
        super().__init__(parent, fg_color=self.config.theme("main_color"))
        self.game_state = game_state
        self.parent = parent

        # Configure grid layout
        self.grid_columnconfigure(tuple(range(11)), weight=1)
        self.grid_rowconfigure(tuple(range(11)), weight=1)

        # Main title
        greet = ctk.CTkLabel(
            self,
            text="MINESWEEPER",
            text_color=self.config.theme("main_label"),
            font=ctk.CTkFont(family="Impact", size=32, weight="bold"),
        )
        greet.grid(row=0, column=5, padx=5, pady=5)

        # Best time display
        ctk.CTkLabel(
            self,
            text="Best time:",
            text_color=self.config.theme("text_color"),
            font=ctk.CTkFont(family="Impact", size=20),
        ).grid(row=2, column=5, padx=5, pady=5)

        # Format and display best time
        ctk.CTkLabel(
            self,
            text=(
                f"{self.config.best_time//60:02d}:{self.config.best_time%60:02d}"
                if self.config.current_diff != "custom"
                and self.config.best_time != 9999
                else "-"
            ),
            text_color=self.config.theme("text_color"),
            font=ctk.CTkFont(family="Impact", size=20),
        ).grid(row=3, column=5, padx=5, pady=5, sticky="n")

        # Start game button
        start_btn = ctk.CTkButton(
            self,
            text="Start Game",
            fg_color=self.config.theme("start_color_fg"),
            text_color=self.config.theme("start_color_text"),
            hover_color=self.config.theme("start_color_hover"),
            command=self.start_game,
        )
        start_btn.grid(row=4, column=3, rowspan=1, columnspan=5, sticky="nsew")

        # Settings button
        config_btn = ctk.CTkButton(
            self,
            text="Settings",
            fg_color=self.config.theme("settings_color_fg"),
            text_color=self.config.theme("settings_color_text"),
            hover_color=self.config.theme("settings_color_hover"),
            command=self.configuration,
        )
        config_btn.grid(row=6, column=3, rowspan=1, columnspan=5, sticky="nsew")

        # Exit button
        ctk.CTkButton(
            self,
            text="Exit",
            fg_color=self.config.theme("exit_color_mainmenu"),
            text_color=self.config.theme("exit_color_text"),
            hover_color=self.config.theme("exit_color_hover"),
            command=self.parent.destroy,
        ).grid(row=8, column=3, rowspan=1, columnspan=5, sticky="nsew")

    def configuration(self):
        """Open the configuration/settings screen."""
        self.grid_remove()
        configure_frame = ConfigFrame(self.parent, self.config)
        configure_frame.grid(row=0, column=0, sticky="nsew")

    def start_game(self):
        """
        Start a new game by transitioning to the game screen.
        Calculates appropriate button size based on field dimensions.
        """
        self.grid_remove()
        self.game_state.first_click = True
        width = self.config.width
        height = self.config.height
        pxsquare = width * height

        # Calculate button size based on total number of cells
        if pxsquare < 100:
            self.buttonsize = 48
        elif pxsquare < 260:
            self.buttonsize = 32
        else:
            self.buttonsize = 24

        # Adjust window size to fit the game field
        self.parent.geometry(
            f"{width*self.buttonsize+20}x{height*self.buttonsize + 60}"
        )
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Create main game window
        game_window = ctk.CTkFrame(
            self.parent, fg_color=self.config.theme("main_color")
        )
        game_window.grid(row=0, column=0, sticky="nsew")
        game_window.grid_columnconfigure(0, weight=1)
        game_window.grid_rowconfigure(0, weight=4)  # Info section (top)
        game_window.grid_rowconfigure(1, weight=6)  # Game field (bottom)

        # Create info and field frames
        info_frame = InfoFrame(game_window, self.config, self.game_state)
        field_frame = FieldFrame(
            game_window, self.config, self.buttonsize, info_frame, self.game_state, self
        )

        info_frame.grid(row=0, column=0, rowspan=1, sticky="nsew")
        field_frame.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")


class ConfigFrame(ctk.CTkFrame):
    """Configuration screen for game settings including difficulty and theme selection."""

    def __init__(self, parent, config):
        self.config = config
        super().__init__(parent, fg_color=self.config.theme("main_color"))
        self.parent = parent

        # Configure grid layout
        self.grid_rowconfigure(tuple(range(20)), weight=1)
        self.grid_columnconfigure(tuple(range(20)), weight=1)

        # Initialize selection variables
        self.selected_theme = ctk.StringVar(value=self.config.config["current_theme"])
        self.selected_diff = ctk.StringVar(value=self.config.config["current_diff"])

        # Difficulty selection section
        ctk.CTkLabel(
            self, text="difficulty:", text_color=self.config.theme("text_color")
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

        # Difficulty radio buttons
        ctk.CTkRadioButton(
            self,
            text="easy",
            variable=self.selected_diff,
            value="easy",
            text_color=self.config.theme("text_color"),
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=20)

        ctk.CTkRadioButton(
            self,
            text="normal",
            variable=self.selected_diff,
            value="normal",
            text_color=self.config.theme("text_color"),
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=20)

        ctk.CTkRadioButton(
            self,
            text="hard",
            variable=self.selected_diff,
            value="hard",
            text_color=self.config.theme("text_color"),
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=20)

        ctk.CTkRadioButton(
            self,
            text="custom",
            variable=self.selected_diff,
            value="custom",
            text_color=self.config.theme("text_color"),
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=20)

        # Theme selection radio buttons
        ctk.CTkRadioButton(
            self,
            text="dark",
            variable=self.selected_theme,
            value="dark",
            text_color=self.config.theme("text_color"),
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=20)

        ctk.CTkRadioButton(
            self,
            text="light",
            variable=self.selected_theme,
            value="light",
            text_color=self.config.theme("text_color"),
        ).grid(row=7, column=5, columnspan=2, sticky="w", padx=20)

        # Custom difficulty settings
        self.custom_height = ctk.StringVar(
            value=str(self.config.config["difficulties"]["custom"]["height"])
        )
        self.custom_width = ctk.StringVar(
            value=str(self.config.config["difficulties"]["custom"]["width"])
        )
        self.custom_mines = ctk.StringVar(
            value=str(self.config.config["difficulties"]["custom"]["mines"])
        )

        # Custom settings section
        ctk.CTkLabel(
            self,
            text="Custom difficulty settings:",
            text_color=self.config.theme("text_color"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=1, column=8, columnspan=4, sticky="w", padx=10)

        # Custom settings labels and entry fields
        ctk.CTkLabel(
            self, text="Height:", text_color=self.config.theme("text_color")
        ).grid(row=2, column=8, sticky="w", padx=10)

        ctk.CTkLabel(
            self, text="Width:", text_color=self.config.theme("text_color")
        ).grid(row=3, column=8, sticky="w", padx=10)

        ctk.CTkLabel(
            self, text="Mines:", text_color=self.config.theme("text_color")
        ).grid(row=4, column=8, sticky="w", padx=10)

        # Entry fields for custom settings
        ctk.CTkEntry(
            self,
            textvariable=self.custom_height,
            width=80,
            placeholder_text="Height",
        ).grid(row=2, column=10, sticky="ew", padx=5)

        ctk.CTkEntry(
            self,
            textvariable=self.custom_width,
            width=80,
            placeholder_text="Width",
        ).grid(row=3, column=10, sticky="ew", padx=5)

        ctk.CTkEntry(
            self,
            textvariable=self.custom_mines,
            width=80,
            placeholder_text="Mines",
        ).grid(row=4, column=10, sticky="ew", padx=5)

        # Control buttons
        apply_btn = ctk.CTkButton(
            self,
            text="Apply",
            fg_color=self.config.theme("config_buttons_color"),
            text_color=self.config.theme("config_buttons_text"),
            hover_color=self.config.theme("config_buttons_hover"),
            width=100,
            height=40,
            command=self.apply_settings,
        )
        apply_btn.grid(row=18, column=12, padx=5, pady=5, sticky="")

        OK_btn = ctk.CTkButton(
            self,
            text="OK",
            fg_color=self.config.theme("config_buttons_color"),
            text_color=self.config.theme("config_buttons_text"),
            hover_color=self.config.theme("config_buttons_hover"),
            width=100,
            height=40,
            command=self.ok_settings,
        )
        OK_btn.grid(row=18, column=10, padx=5, pady=5, sticky="")

        exit_btn = ctk.CTkButton(
            self,
            text="Exit",
            fg_color=self.config.theme("config_buttons_color"),
            text_color=self.config.theme("config_buttons_text"),
            hover_color=self.config.theme("config_buttons_hover"),
            width=100,
            height=40,
            command=self.exit_config,
        )
        exit_btn.grid(row=18, column=8, padx=5, pady=5, sticky="")

    def apply_settings(self):
        """
        Apply current settings to configuration.
        Validates custom difficulty inputs and shows error dialogs if needed.
        """
        try:
            # Update basic settings
            self.config.config["current_diff"] = self.selected_diff.get()
            self.config.config["current_theme"] = self.selected_theme.get()

            # Validate and update custom difficulty settings
            if self.selected_diff.get() == "custom":
                height_str = self.custom_height.get()
                width_str = self.custom_width.get()
                mines_str = self.custom_mines.get()

                # Check if all inputs are numeric
                if not (
                    height_str.isdigit() and width_str.isdigit() and mines_str.isdigit()
                ):
                    raise ValueError("Height, Width and Mines must be numeric")

                height = int(height_str.strip())
                width = int(width_str.strip())
                mines = int(mines_str.strip())

                if height < 4 or width < 4 or height > 100 or width > 100:
                    raise ValueError(
                        "The field is too small or big. Min/max value is 4/100."
                    )
                # Validate that mines count is reasonable
                if mines >= width * height * 0.8 - 9:
                    raise ValueError(
                        "Mines count must be less than Width * Height * 0.8 - 9(for safe zone)."
                    )
                if mines < 1:
                    raise ValueError("Too few mines")

                # Update custom difficulty configuration
                self.config.config["difficulties"]["custom"]["height"] = height
                self.config.config["difficulties"]["custom"]["width"] = width
                self.config.config["difficulties"]["custom"]["mines"] = mines

            # Save configuration to file
            with open("config.json", "w") as f:
                json.dump(self.config.config, f, indent=2)
            self.config.reload_config()

        except ValueError as e:
            # Show error dialog for validation errors
            print(f"Error: Invalid input values - {e}")
            self._show_error_dialog(str(e))
        except Exception as e:
            # Show error dialog for other errors
            print(f"Error applying settings: {e}")
            self._show_error_dialog(str(e))

    def _show_error_dialog(self, error_message):
        """
        Show error dialog with given message.

        Args:
            error_message (str): Error message to display
        """
        error_box = ctk.CTkToplevel(self, fg_color="#F8D7DA")
        error_box.title("ERROR")
        error_box.geometry("300x100")
        error_box.grid_columnconfigure(0, weight=1)
        error_box.grid_rowconfigure((0, 1), weight=1)
        ctk.CTkLabel(error_box, text=error_message, wraplength=240).grid(
            row=0, column=0
        )
        ctk.CTkButton(
            error_box,
            text="OK",
            fg_color=self.config.theme("exit_color_mainmenu"),
            command=error_box.destroy,
        ).grid(row=1, column=0, sticky="e")

    def ok_settings(self):
        """Apply settings and exit configuration screen."""
        self.apply_settings()
        self.exit_config()

    def exit_config(self):
        """Exit configuration screen and return to main menu."""
        self.grid_remove()
        self.parent.build_ui()


class InfoFrame(ctk.CTkFrame):
    """Information panel showing difficulty, mine count, and game timer."""

    def __init__(self, parent, config, game_state):
        self.config = config
        super().__init__(parent, fg_color=self.config.theme("main_color"))
        self.game_state = game_state

        # Configure grid layout
        self.grid_rowconfigure(tuple(range(4)), weight=1)
        self.grid_columnconfigure(tuple(range(10)), weight=1)

        # Display current difficulty
        difficulty = ctk.CTkLabel(
            self,
            text=self.config.current_diff,
            text_color=self.config.theme("text_color"),
        )
        difficulty.grid(row=3, column=0, sticky="nsew")

        # Display mine count
        self.mines_label = ctk.CTkLabel(
            self,
            text=f"Bombs: {self.game_state.mines}",
            text_color=self.config.theme("text_color"),
        )
        self.mines_label.grid(row=3, column=5, padx=0, pady=5, sticky="nsew")

        # Display game timer
        self.timer = ctk.CTkLabel(
            self, text="00:00", text_color=self.config.theme("text_color")
        )
        self.timer.grid(row=3, column=9, sticky="nsew")

    def start_timer(self):
        """Start the game timer if not already running."""
        if not self.game_state.running:
            self.game_state.running = True
            self.update_timer()

    def stop_timer(self):
        """Stop the game timer."""
        self.game_state.running = False

    def reset_timer(self):
        """Reset timer display to 00:00."""
        self.timer.configure(text="00:00")

    def update_timer(self):
        """
        Update timer display and schedule next update.
        Updates every second while game is running.
        """
        if self.game_state.running:
            time = self.game_state.update_timer()
            if time is not None:
                # Format time as MM:SS
                minutes = self.game_state.time_elapsed // 60
                seconds = self.game_state.time_elapsed % 60
                self.timer.configure(text=f"{minutes:02d}:{seconds:02}")
                # Schedule next update in 1 second
                self.after(1000, self.update_timer)


class FieldFrame(ctk.CTkFrame):
    """Game field frame containing the grid of cell buttons for gameplay."""

    def __init__(self, parent, config, buttonsize, info_frame, game_state, root_parent):
        self.config = config
        """
        Initialize the game field with a grid of buttons linked to game state.

        Args:
            parent: Parent widget containing this frame
            config: Configuration object with game settings
            buttonsize (int): Size of each button in pixels
            info_frame: InfoFrame object for timer and mine count display
            game_state: GameState object managing game logic
            root_parent: Root parent (GreetScreen) for navigation
        """
        super().__init__(parent, fg_color=self.config.theme("main_color"))
        self.buttonsize = buttonsize
        self.info_frame = info_frame
        self.game_state = game_state
        self.root_parent = root_parent
        self.cur_dif = self.config.current_diff

        # Initialize 2D array for buttons
        self.buttons = [
            [None for _ in range(self.config.width)] for _ in range(self.config.height)
        ]

        # Create game field in game state
        self.game_state.do_field(self.buttons, self)

        # Create and place buttons for each cell
        for row in range(self.config.height):
            for col in range(self.config.width):
                btn = ctk.CTkButton(
                    self,
                    width=self.buttonsize,
                    height=self.buttonsize,
                    corner_radius=0,
                    text="",
                    fg_color=self.config.theme("button_color"),
                    text_color=self.config.theme("text_color"),
                    hover_color=self.config.theme("hover_color"),
                )
                btn.grid(row=row, column=col, padx=0, pady=0)

                # Bind left-click to cell reveal
                btn.configure(command=lambda r=row, c=col: self.on_click(r, c))

                # Bind right-click to flag placement
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.set_flag(r, c))
                self.buttons[row][col] = btn

    def on_click(self, row, col):
        """
        Handle left-click on a cell to reveal it and initialize field on first click.

        Args:
            row (int): Row coordinate of the clicked cell
            col (int): Column coordinate of the clicked cell
        """
        if self.game_state.first_click:
            # Initialize safe zone and place bombs on first click
            self.game_state.safe_zone(row, col)
            self.game_state.first_click = False
            self.game_state.place_bombs()
            self.game_state.calculate_neighbor_bombs()
            self.info_frame.start_timer()
            # Auto-reveal cells in safe zone
            for dc in [-1, 0, 1]:
                for dr in [-1, 0, 1]:
                    new_r = row + dr
                    new_c = col + dc
                    if (
                        0 <= new_c < self.config.width
                        and 0 <= new_r < self.config.height
                    ):
                        self.game_state.field[new_r][new_c].reveal()
        else:
            # Reveal clicked cell
            self.game_state.field[row][col].reveal()

    def set_flag(self, row, col):
        """
        Toggle flag on a cell with right-click and update mine count display.

        Args:
            row (int): Row coordinate of the cell
            col (int): Column coordinate of the cell
        """
        if not self.game_state.field[row][col].revealed:
            # Toggle flag state
            self.game_state.field[row][col].flagged = not self.game_state.field[row][
                col
            ].flagged
            if self.game_state.field[row][col].flagged:
                # Set flag color and decrease mine count
                self.buttons[row][col].configure(
                    fg_color=self.config.theme("flag_color")
                )
                self.game_state.mines -= 1
                # Update mine count label
                self.info_frame.mines_label.configure(
                    text=(
                        f"Bombs: {self.game_state.mines}"
                        if self.game_state.mines >= 0
                        else "Are you dumb?"
                    )
                )
            else:
                # Remove flag and restore button color
                self.buttons[row][col].configure(
                    fg_color=self.config.theme("button_color")
                )
                self.game_state.mines += 1
                # Update mine count label
                self.info_frame.mines_label.configure(
                    text=(
                        f"Bombs: {self.game_state.mines}"
                        if self.game_state.mines >= 0
                        else "Are you dumb?"
                    )
                )


class Cell:
    """Represents a single cell in the Minesweeper game field."""

    def __init__(
        self,
        parent,
        col,
        row,
        config,
        app,
        field_frame,
        bomb=False,
        revealed=False,
        flagged=False,
        neighbor_bombs=0,
    ):
        """
        Initialize a cell with position and state.

        Args:
            parent: GameState object managing the cell
            col (int): Column coordinate
            row (int): Row coordinate
            config: Configuration object with game settings
            app: Main application instance
            field_frame: FieldFrame containing the cell's button
            bomb (bool): Whether the cell contains a mine
            revealed (bool): Whether the cell is revealed
            flagged (bool): Whether the cell is flagged
            neighbor_bombs (int): Number of adjacent mines
        """
        self.field_frame = field_frame
        self.app = app
        self.parent = parent
        self.config = config
        self.col = col
        self.row = row
        self.bomb = bomb
        self.revealed = revealed
        self.flagged = flagged
        self.neighbor_bombs = neighbor_bombs

    def reveal(self):
        """Reveal the cell and handle game outcomes or propagate reveals."""
        if not self.bomb and not self.revealed:
            if not self.flagged:
                # Mark cell as revealed and remove from unrevealed list
                self.revealed = True
                self.parent.all_cords.remove(self.row * self.config.width + self.col)

                # Update button appearance
                self.parent.buttons[self.row][self.col].configure(
                    fg_color=self.config.theme("pressed_color")
                )

                if self.neighbor_bombs >= 1:
                    # Set number color based on adjacent bombs
                    num_color = self.config.theme("num_colors").get(
                        str(self.neighbor_bombs),
                        self.config.theme("text_color"),
                    )
                    self.parent.buttons[self.row][self.col].configure(
                        text_color=num_color
                    )
                    self.parent.buttons[self.row][self.col].configure(
                        text=self.neighbor_bombs
                    )

                if not self.parent.all_cords:
                    # Trigger win condition if all non-mine cells are revealed
                    EndGamePopup(self.app, self.config, self.parent, self.field_frame)
                    self.parent.check_best()
                    self.field_frame.info_frame.stop_timer()

                if self.neighbor_bombs == 0:
                    # Recursively reveal adjacent cells if no nearby bombs
                    for dc in [-1, 0, 1]:
                        for dr in [-1, 0, 1]:
                            new_r = self.row + dr
                            new_c = self.col + dc
                            if (
                                0 <= new_c < self.config.width
                                and 0 <= new_r < self.config.height
                                and not self.parent.field[new_r][new_c].revealed
                            ):
                                self.parent.field[new_r][new_c].reveal()

        elif self.revealed:
            # Attempt chord action if already revealed
            self.try_chord()

        elif self.bomb and not self.flagged:
            # Trigger loss condition if mine is revealed
            EndGamePopup(
                self.app,
                self.config,
                self.parent,
                self.field_frame,
                win=False,
            )
            self.field_frame.info_frame.stop_timer()
            self.parent.buttons[self.row][self.col].configure(
                fg_color=self.config.theme("mines_color")
            )

    def try_chord(self):
        """
        Attempt a chord action by revealing neighbors if flagged count matches adjacent bombs.
        Only works on revealed cells with a number.
        """
        if not self.revealed:
            return

        # Count flagged neighbors
        flagged_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = self.row + dr, self.col + dc
                if 0 <= nr < self.config.height and 0 <= nc < self.config.width:
                    if self.parent.field[nr][nc].flagged:
                        flagged_count += 1

        # Reveal neighbors if flagged count matches adjacent bombs
        if flagged_count == self.neighbor_bombs:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = self.row + dr, self.col + dc
                    if 0 <= nr < self.config.height and 0 <= nc < self.config.width:
                        if (
                            not self.parent.field[nr][nc].revealed
                            and not self.parent.field[nr][nc].flagged
                        ):
                            self.parent.field[nr][nc].reveal()


class EndGamePopup(ctk.CTkToplevel):
    """Popup window displayed when the game ends, showing win or loss message."""

    def __init__(self, app, config, game_state, field_frame, win=True):
        """
        Initialize the end game popup with win or loss message and navigation options.

        Args:
            app: Main application instance
            config: Configuration object with game settings
            game_state: GameState object managing game logic
            field_frame: FieldFrame containing the game field
            win (bool): Whether the game was won or lost
        """
        self.config = config
        super().__init__()
        self.app = app
        self.field_frame = field_frame
        self.game_state = game_state
        self.title("You won!" if win else "You lost!")
        self.geometry("400x150")
        self.configure(fg_color="#D4EDDA" if win else "#F8D7DA")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Display win or loss message
        label = ctk.CTkLabel(
            self,
            text=(
                "You've passed the minesweeper test"
                if win
                else "You were blown up by a mine, my friend"
            ),
            text_color=self.config.theme("text_color"),
            fg_color=self.config.theme("main_color"),
        )
        label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Exit button to close application
        exit_btn = ctk.CTkButton(
            self,
            text="✗ Exit ✗",
            command=self.app.destroy,
            fg_color=self.config.theme("exit_color_mainmenu"),
            text_color=self.config.theme("exit_color_text"),
            hover_color=self.config.theme("exit_color_hover"),
            corner_radius=0,
        )
        exit_btn.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Main menu button to return to start screen
        main_menu_btn = ctk.CTkButton(
            self,
            text="❖ Main Menu ❖",
            fg_color=self.config.theme("settings_color_fg"),
            text_color=self.config.theme("settings_color_text"),
            hover_color=self.config.theme("settings_color_hover"),
            corner_radius=0,
            command=self.main_menu,
        )
        main_menu_btn.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        # New game button to restart game
        new_game_btn = ctk.CTkButton(
            self,
            text="➕ New Game ➕",
            fg_color=self.config.theme("start_color_fg"),
            text_color=self.config.theme("start_color_text"),
            hover_color=self.config.theme("start_color_hover"),
            corner_radius=0,
            command=self.new_game,
        )
        new_game_btn.grid(row=1, column=2, sticky="nsew", padx=0, pady=0)

    def new_game(self):
        """Start a new game by resetting state and reopening game screen."""
        self.destroy()
        self.game_state.reset_game()
        self.field_frame.root_parent.start_game()

    def main_menu(self):
        """Return to the main menu by resetting state and rebuilding UI."""
        self.destroy()
        self.game_state.reset_game()
        self.app.build_ui()


app = MinesweeperApp()
app.mainloop()
