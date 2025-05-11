from rich_pixels import Pixels, Renderer
from textual.widgets import Static


class Image(Static):
    def __init__(self, image_path: str, resize: tuple[int, int] = None, renderer: Renderer = None, name = None, id = None, classes = None):
        self.image_path = image_path
        self.resize = resize
        self.renderer = renderer

        self.pixels = Pixels.from_image_path(self.image_path, self.resize, self.renderer)

        super().__init__(self.pixels, id=id, name=name, classes=classes)