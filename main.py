import customtkinter as ctk

PROGRAM_NAME = 'Atlas Protocol'
PROGRAM_VERSION = 'v0.1'

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 750
PANEL_CONTROL_WIDTH = 300
PANEL_BOM_WIDTH = 300
PANEL_DRAWING_HEIGHT = 200

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')


class AtlasProtocol(ctk.CTk):
    """
    Main GUI application window for the Atlas Protocol system.

    This window serves as the central hub for logic-driven mechanical resolution,
    including UI panels for:
        - Parameterized input and control (left)
        - Real-time 3D model viewer (center)
        - Resolved BOM overview (right)
        - Drawing/export previews (bottom)

    Designed as a logic-first interface for interacting with declarative part definitions,
    structure resolution, and digital twin output.

    Layout is modular, grid-based, and scalable for future extensions like:
        - Module selection dropdowns
        - CSV input triggers
        - Viewer → Code navigation
        - Export and ERP linkage

    This class defines the UI shell. Functional logic is executed via embedded modules.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title(f'{PROGRAM_NAME} {PROGRAM_VERSION}')
        self.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self._center_screen()
        self._configure_grid()
        self._build_layout()

    def _center_screen(self) -> None:
        """ Gets the coordinates of the center of the screen and moves GUI. """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (WINDOW_WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")

    def _configure_grid(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

    def _build_layout(self) -> None:
        # Top left (Control Panel)
        self.frame_control = ctk.CTkFrame(self, width=PANEL_CONTROL_WIDTH)
        self.frame_control.grid(row=0, column=0, sticky='nsw', padx=5, pady=5)

        # Top center (3D Viewer)
        self.frame_3d_viewer = ctk.CTkFrame(self)
        self.frame_3d_viewer.grid(row=0, column=1, sticky='nsew', padx=5,
                                  pady=5)

        # Top right (BOM List)
        self.frame_bom = ctk.CTkFrame(self, width=PANEL_BOM_WIDTH)
        self.frame_bom.grid(row=0, column=2, sticky='nse', padx=5, pady=5)

        # Bottom row (Drawing previews)
        self.frame_drawings = ctk.CTkFrame(self, height=PANEL_DRAWING_HEIGHT)
        self.frame_drawings.grid(row=1, column=0, columnspan=3, sticky='ew',
                                 padx=5, pady=5)


if __name__ == '__main__':
    app = AtlasProtocol()
    app.mainloop()
