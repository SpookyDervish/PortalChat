from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, Container, Center, Right
from textual.widgets import Label, Button, Input, Rule, TabbedContent, TabPane

from ui.widgets.image import Image

import configparser, os


class SettingsScreen(ModalScreen):
    DEFAULT_CSS = """
    SettingsScreen {
        align: center middle;

        Rule {
            color: $background-lighten-2;
        }

        #window {
            max-width: 50%;
            max-height: 75%;
            border: panel $primary;
            border-title-align: center;

            TabbedContent {
                margin: 1;
            }
        }

        .title {
            text-style: bold underline;
            padding: 1;
            margin: 0 1;
            width: 100%;
        }

        #user-box {
            margin: 1;
            max-height: 15;
            background: $boost;
            border: tall $background-lighten-2;
        }

        #user-icon {
            max-width: 6;
            max-height: 6;
            margin-right: 1;
            margin-left: 2;
        }

        #user-name {
            height: 3;
            content-align: left middle;
            text-style: bold;
        }

        #edit-user-btn {
            dock: right;
            margin-right: 2;
        }

        Center {
            dock: bottom;
            max-height: 70%;
        }

        #user-details {
            background: $boost-lighten-2;
            
            margin-left: 2;
            margin-right: 2;

            padding: 1;
        }

        .info-container {
            height: 3;
            margin-bottom: 1;
            
            Button {
                dock: right;
            }
        }

        .detail-title {
            margin: 1 0;
        }

        #edit-details {
            margin: 1;
        }

        Right {
            dock: bottom;
        }
    }
    """

    def __init__(self, name = None, id = None, classes = None):
        super().__init__(name, id, classes)
        self.config = configparser.ConfigParser()
        if not os.path.isfile('user_settings.ini'):
            self.init_settings_file()
        else:
            self.config.read("user_settings.ini")

        if not os.path.isfile(self.config.get("MyAccount", "icon_path")):
            self.config.set("MyAccount", "icon_path", os.path.abspath("assets/images/default_user.png"))
            self.save_settings()

    def init_settings_file(self):
        self.config["MyAccount"] = {
            "username": "user",
            "icon_path": os.path.abspath("assets/images/default_user.png")
        }
        self.save_settings()
        
    def save_settings(self):
        with open('user_settings.ini', "w") as config_file:
            self.config.write(config_file)

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss()

    def on_button_pressed(self, event):
        button: Button = event.button

        if "edit" in button.classes:
            self.query_one("#user-box").display = 'none'
            self.query_one('#edit-details').display = "block"
        elif button.id == "save":
            self.notify("Settings saved!")
            self.save_settings()

            user_name = self.config.get("MyAccount", "username")

            # update ui elements with new data
            self.query_one("#username-label").update(user_name)
            self.query_one("#user-name").update(user_name)
            self.query_one("#username-input").placeholder = user_name

            # go back to main page
            self.query_one("#user-box").display = 'block'
            self.query_one('#edit-details').display = "none"

    def on_input_changed(self, event):
        if event.input.id == "username-input":
            self.config["MyAccount"]["username"] = event.input.value

    def compose(self):
        user_name = self.config.get("MyAccount", "username")

        with Vertical(id="window") as window:
            window.border_title = "=== Settings ==="

            with TabbedContent():
                with TabPane("My Account"):
                    yield Label("My Account", classes="title", variant="primary")
                    yield Rule()

                    with Horizontal(id="user-box"):
                        yield Image("assets/images/default_user.png", (6,6), id="user-icon")
                        yield Label(user_name, id="user-name")
                        yield Button("Edit User Profile", variant="primary", id="edit-user-btn", classes="edit")

                        with Center():
                            with Vertical(id="user-details"):
                                with Container(classes="info-container"):
                                    yield Label("[b]Username")
                                    yield Label(user_name, id="username-label")
                                    yield Button("Edit", classes="edit")
                    

                    with Vertical(id="edit-details") as edit:
                        edit.display = "none"
                        yield Label("[b]Usernanme", classes="detail-title")
                        yield Input(user_name, placeholder=user_name, max_length=25, valid_empty=False, id="username-input")

                        yield Label("[b]Avatar", classes="detail-title")
                        yield Button("Change Avatar", variant="primary")

                        with Right():
                            yield Button("Save", variant="primary", id="save")