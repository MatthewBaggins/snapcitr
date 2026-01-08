from datetime import datetime
import os
import time
import tkinter as tk
import typing as typ

from PIL import ImageGrab
from PIL.Image import Image
from pynput import keyboard


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
        "_root",
        "_hidden",
        "_alt_pressed_alone",
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
        self._root: tk.Tk | None = None
        self._hidden: bool = False
        self._alt_pressed_alone: bool = False

    def start_selection(self, *, delay_seconds: int = 0) -> None:
        """Open a fullscreen window for rectangle selection

        Controls:
            - Click and drag to select area
            - Press Alt alone (not combo) to hide/show overlay
            - Press Escape to cancel
        """
        if delay_seconds > 0:
            print(f"Starting in {delay_seconds} seconds... Prepare your screen.")
            for i in range(delay_seconds, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            print("Go!")

        print(
            "Controls: Alt (alone) = hide/show overlay | Esc = cancel | Click+drag = select"
        )

        self._root = tk.Tk()
        self._root.attributes("-type", "splash")  # Make window borderless
        self._root.attributes("-alpha", 0.3)  # Semi-transparent
        self._hidden = False

        # Get screen dimensions
        self.screen_width = self._root.winfo_screenwidth()
        self.screen_height = self._root.winfo_screenheight()

        # Set geometry to cover entire screen
        self._root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self._root.attributes("-fullscreen", True)

        canvas = tk.Canvas(self._root, bg="white", highlightthickness=0)
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

        def on_release(_: tk.Event) -> None:
            self.selected = True
            if self._root:
                self._root.quit()

        def on_key(event: tk.Event) -> None:
            if event.keysym == "Escape":
                self.selected = False
                if self._root:
                    self._root.quit()

        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        self._root.bind("<Key>", on_key)

        # Global hotkey listener for Alt alone and Escape
        def on_global_key_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self._alt_pressed_alone = True
            elif key == keyboard.Key.esc:
                # Escape always exits, even if overlay is hidden
                self.selected = False
                if self._root:
                    self._root.after(0, self._root.quit)

        def on_global_key_release(key: keyboard.Key | keyboard.KeyCode | None) -> None:
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                if self._alt_pressed_alone and self._root:
                    # Toggle overlay visibility
                    self._root.after(0, self._toggle_overlay)
            else:
                # Another key was pressed, so Alt is a combo
                self._alt_pressed_alone = False

        listener = keyboard.Listener(
            on_press=on_global_key_press,
            on_release=on_global_key_release,
        )
        listener.start()

        self._root.mainloop()

        listener.stop()
        self._root.destroy()
        self._root = None

    def _toggle_overlay(self) -> None:
        """Toggle overlay visibility"""
        if self._root is None:
            return
        if self._hidden:
            self._root.deiconify()
            self._root.lift()
            self._root.focus_force()
            self._hidden = False
            print("Overlay shown. Alt = hide | Click+drag = select")
        else:
            self._root.withdraw()
            self._hidden = True
            print("Overlay hidden. Alt = show overlay")

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

        # Longer delay to ensure overlay is fully cleared and focus is restored
        time.sleep(0.2)
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
