from datetime import datetime
import os
import time
import tkinter as tk
import typing as typ

from PIL import ImageGrab
from PIL.Image import Image


class RectangleSelector:
    __slots__ = (
        "x1",
        "y1",
        "x2",
        "y2",
        "rect",
        "selected",
        "screen_width",
        "screen_height",
    )

    def __init__(self) -> None:
        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        self.rect: int | None = None
        self.selected: bool = False
        self.screen_width: int | None = None
        self.screen_height: int | None = None

    def start_selection(self) -> None:
        """Open a fullscreen window for rectangle selection"""
        root = tk.Tk()
        root.attributes("-type", "splash")  # Make window borderless
        root.attributes("-alpha", 0.3)  # Semi-transparent

        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # Set geometry to cover entire screen
        root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        root.attributes("-fullscreen", True)

        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        def on_press(event: tk.Event) -> None:
            self.x1 = event.x
            self.y1 = event.y

        def on_drag(event: tk.Event) -> None:
            self.x2 = event.x
            self.y2 = event.y

            # Redraw rectangle
            if self.rect:
                canvas.delete(self.rect)

            self.rect = canvas.create_rectangle(
                self.x1, self.y1, self.x2, self.y2, outline="red", width=2
            )

        def on_release(event: tk.Event) -> None:
            self.selected = True
            root.destroy()

        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

        root.mainloop()

    def get_coordinates(self) -> tuple[int, int, int, int]:
        """Return normalized coordinates"""
        x1 = min(self.x1, self.x2)
        y1 = min(self.y1, self.y2)
        x2 = max(self.x1, self.x2)
        y2 = max(self.y1, self.y2)
        return (x1, y1, x2, y2)

    @typ.overload
    def capture_image(self, *, strict: typ.Literal[False]) -> Image | None: ...
    @typ.overload
    def capture_image(self, *, strict: typ.Literal[True]) -> Image: ...

    def capture_image(self, *, strict: bool = False) -> Image | None:
        if not self.selected:
            print("No region selected.")
            return

        time.sleep(0.1)
        bbox = self.get_coordinates()
        snapshot = ImageGrab.grab(bbox=bbox)
        if strict:
            assert snapshot is not None
        return snapshot

    def save(self, img: Image) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(os.getcwd(), f"snapshot_{timestamp}.png")
        img.save(save_path)
        print(f"Snapshot saved at {save_path}")

    def capture_and_save(self) -> None:
        """Capture the selected region and save it"""
        img = self.capture_image(strict=True)
        self.save(img)
