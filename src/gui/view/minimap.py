import cv2
import tkinter as tk
from tkinter.font import Font
from PIL import ImageTk, Image
from src.gui.interfaces import LabelFrame
from src.common import config, utils
from src.routine.components import Point


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Minimap', **kwargs)

        self.WIDTH = 400
        self.HEIGHT = 300
        self.canvas = tk.Canvas(self, bg='black',
                                width=self.WIDTH, height=self.HEIGHT,
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)
        minimap_desc = tk.Label(self, 
                                text="Recalibrate minimap if not properly displayed",
                                font=(Font(family="TkDefaultFont",size=6,slant="italic"))
                                )
        minimap_desc.pack()
        self.container = None

    def display_minimap(self):
        """Updates the Main page with the current minimap."""

        minimap = config.capture.minimap
        if minimap:
            rune_active = minimap['rune_active']
            rune_pos = minimap['rune_pos']
            path = minimap['path']
            player_pos = minimap['player_pos']

            img = cv2.cvtColor(minimap['minimap'], cv2.COLOR_BGR2RGB)
            height, width, _ = img.shape

            # Resize minimap to fit the Canvas
            ratio = min(self.WIDTH / width, self.HEIGHT / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            if new_height * new_width > 0:
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # Mark the position of the active rune
            if rune_active and rune_pos:
                rune_abs = utils.convert_to_absolute(rune_pos, img)
                cv2.circle(img, rune_abs, 6, (128, 0, 128), -1)  # Purple circle
                cv2.circle(img, rune_abs, 8, (255, 255, 255), 2)  # White outline
                cv2.putText(img, "RUNE", (rune_abs[0] + 10, rune_abs[1]), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 0, 128), 1)

            # Draw the current path that the program is taking
            if config.enabled and len(path) > 1:
                for i in range(len(path) - 1):
                    start = utils.convert_to_absolute(path[i], img)
                    end = utils.convert_to_absolute(path[i + 1], img)
                    cv2.line(img, start, end, (0, 255, 255), 1)

            # Draw each Point in the routine as a circle
            for p in config.routine.sequence:
                if isinstance(p, Point):
                    utils.draw_location(img,
                                        p.location,
                                        (0, 255, 0) if config.enabled else (255, 0, 0))

            # Display the current Layout
            if config.layout:
                config.layout.draw(img)

            # Draw other players (blue circles)
            others_pos = minimap.get('others_pos', [])
            for other_pos in others_pos:
                other_abs = utils.convert_to_absolute(other_pos, img)
                cv2.circle(img, other_abs, 4, (255, 0, 0), -1)  # Blue circle
                cv2.circle(img, other_abs, 6, (255, 255, 255), 1)  # White outline
                cv2.putText(img, "OTHER", (other_abs[0] + 8, other_abs[1]), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

            # Draw the player's position on top of everything
            player_abs = utils.convert_to_absolute(player_pos, img)
            cv2.circle(img, player_abs, 5, (0, 0, 255), -1)  # Larger red circle
            cv2.circle(img, player_abs, 7, (255, 255, 255), 2)  # White outline
            cv2.putText(img, "PLAYER", (player_abs[0] + 10, player_abs[1]), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
            # Add detection status overlay
            status_text = f"Tracking: {'ACTIVE' if config.capture.ready else 'INACTIVE'}"
            cv2.putText(img, status_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                      (0, 255, 0) if config.capture.ready else (0, 0, 255), 2)
            
            # Add player count
            player_count = len(others_pos) + 1
            cv2.putText(img, f"Players: {player_count}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Add rune status
            rune_status = "RUNE: ACTIVE" if rune_active else "RUNE: NONE"
            rune_color = (128, 0, 128) if rune_active else (128, 128, 128)
            cv2.putText(img, rune_status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, rune_color, 1)

            # Display the minimap in the Canvas
            img = ImageTk.PhotoImage(Image.fromarray(img))
            if self.container is None:
                self.container = self.canvas.create_image(self.WIDTH // 2,
                                                          self.HEIGHT // 2,
                                                          image=img, anchor=tk.CENTER)
            else:
                self.canvas.itemconfig(self.container, image=img)
            self._img = img                 # Prevent garbage collection
