import customtkinter as ctk
import os
import json

from viewer.vtk_viewer import VTKViewer

PROGRAM_NAME = 'Atlas Protocol'
PROGRAM_VERSION = 'v0.1'

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 750
PANEL_CONTROL_WIDTH = 300
PANEL_BOM_WIDTH = 300
PANEL_DRAWING_HEIGHT = 200
PANEL_TOP_HEIGHT = 100
MODELS_DIR = './models'

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')


class AtlasProtocol(ctk.CTk):
    """
    Main GUI application window for the Atlas Protocol system.

    This window serves as the central hub for logic-driven mechanical
    resolution, including UI panels for:
        - Parameterized input and control (left)
        - Real-time 3D model viewer (center)
        - Resolved BOM overview (right)
        - Drawing/export previews (bottom)

    Designed as a logic-first interface for interacting with declarative part
    definitions, structure resolution, and digital twin output.

    Layout is modular, grid-based, and scalable for future extensions like:
        - Module selection dropdowns
        - CSV input triggers
        - Viewer → Code navigation
        - Export and ERP linkage

    This class defines the UI shell. Functional logic is executed via embedded
    modules.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title(f'{PROGRAM_NAME} {PROGRAM_VERSION}')
        self.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

        self.models = {}
        self._center_screen()
        self._configure_grid()
        self._build_layout()
        self._scan_and_update_models()

    def _center_screen(self) -> None:
        """ Gets the coordinates of the center of the screen and moves GUI. """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (WINDOW_WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")

    def _configure_grid(self) -> None:
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

    def _build_layout(self) -> None:
        # Top left (Control Panel)
        self.frame_control = ctk.CTkFrame(
            self, width=PANEL_CONTROL_WIDTH, height=PANEL_TOP_HEIGHT)
        self.frame_control.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        self.dropdown_model = ctk.CTkOptionMenu(
            self.frame_control, width=275, anchor='w',
            values=list(self.models.keys()), command=self._on_model_selected)
        self.dropdown_model.place(x=10, y=10)

        self.button_rescan = ctk.CTkButton(
            self.frame_control, text='↻ Rescan Models', anchor='w',
            command=self._scan_and_update_models)
        self.button_rescan.place(x=80, y=50)

        # Top center (3D Viewer - spans vertically across row 0 and 1)
        self.frame_3d_viewer = ctk.CTkFrame(self)
        self.frame_3d_viewer.grid(
            row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)

        self._embed_vtk_viewer()

        # Top right (Assembly details)
        self.frame_details = ctk.CTkFrame(
            self, width=PANEL_BOM_WIDTH, height=PANEL_TOP_HEIGHT)
        self.frame_details.grid(row=0, column=2, sticky='ne', padx=5, pady=5)

        # Mid left (Model settings)
        self.frame_model = ctk.CTkFrame(self, width=PANEL_CONTROL_WIDTH)
        self.frame_model.grid(row=1, column=0, sticky='nsw', padx=5, pady=5)

        # Mid right (BOM List)
        self.frame_bom = ctk.CTkFrame(self, width=PANEL_BOM_WIDTH)
        self.frame_bom.grid(row=1, column=2, sticky='nse', padx=5, pady=5)

        # Bottom row (Drawing previews)
        self.frame_drawings = ctk.CTkFrame(self, height=PANEL_DRAWING_HEIGHT)
        self.frame_drawings.grid(
            row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    def _on_model_selected(self, choice: str) -> None:
        print(f'Selected model: {choice}')
        config = self.models.get(choice, {}).get('config', {})
        print(json.dumps(config, indent=2))
        # TODO: Clear and repopulate self.frame_model with settings

    def _scan_and_update_models(self) -> None:
        """ Scan the models folder and populate the selector dropdown. """
        self.models.clear()
        if not os.path.isdir(MODELS_DIR):
            os.makedirs(MODELS_DIR)

        for entry in os.scandir(MODELS_DIR):
            if entry.is_dir():
                config_path = os.path.join(entry.path, 'config.json')
                if os.path.isfile(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read()
                            data = json.loads(content)
                            model_name = data.get('name', entry.name)
                            self.models[model_name] = {
                                'folder': entry.name,
                                'config': data
                            }
                    except Exception as e:
                        print(f'Error loading {entry.name}: {e}')

        # Update dropdown if it exists
        if hasattr(self, 'dropdown_model'):
            self.dropdown_model.configure(values=list(self.models.keys()))
            if self.models:
                self.dropdown_model.set(next(iter(self.models)))
            else:
                self.dropdown_model.set('No models found')

    def _embed_vtk_viewer(self):
        """ Embed VTK viewer into the center frame. """
        native_tk_frame = self.frame_3d_viewer
        self.vtk_viewer = VTKViewer(native_tk_frame, width=900, height=700)
        self.vtk_viewer.pack(fill='both', expand=True)

        # Load the demo STL file
        stl_path = os.path.join('models', 'atlas_test_cube', 'cube.stl')
        if os.path.isfile(stl_path):
            self.vtk_viewer.load_stl(stl_path)


if __name__ == '__main__':
    app = AtlasProtocol()
    app.mainloop()
