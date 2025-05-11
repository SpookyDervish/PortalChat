from textual.containers import Vertical
from textual.widgets import Static, Markdown, Rule
from rich.text import Text


class Welcome(Vertical):
    DEFAULT_CSS = """
    Welcome {
        align: center middle;

        .title {
            text-align: center;
            min-width: 50%;
            width: auto;
        }

        #welcome-msg {
            width: 50%;
            min-width: 54;
            align-horizontal: center;
            background: $background;
        }

        Rule {
            min-width: 54;
            width: 50% !important;
            
            color: $background-lighten-3;
        }
    }
    """

    WELCOME_MD = """# Welcome!
**Portal** is a *somewhat* well made chat app, designed to be used as a replacement to `Discord` where you can't use it. ;)

# How do I use Portal?
It's simple! In the bottom left, click on the **"+"** button, this is where you can add servers! Portal **will automatically find servers for you** on your local network, and you can tell Portal to remember them!"""
    
    
    COLOURS = [
        "#881177",
        "#aa3355",
        "#cc6666",
        "#ee9944",
        "#eedd00",
        "#99dd55",
        "#44dd88",
        "#22ccbb",
        "#00bbcc",
        "#0099cc",
        "#3366bb",
        "#663399",
    ]

    TITLE = rf"""
                                 __                __ 
                                /  |              /  |
  ______    ______    ______   _$$ |_     ______  $$ |
 /      \  /      \  /      \ / $$   |   /      \ $$ |
/$$$$$$  |/$$$$$$  |/$$$$$$  |$$$$$$/    $$$$$$  |$$ |
$$ |  $$ |$$ |  $$ |$$ |  $$/   $$ | __  /    $$ |$$ |
$$ |__$$ |$$ \__$$ |$$ |        $$ |/  |/$$$$$$$ |$$ |
$$    $$/ $$    $$/ $$ |        $$  $$/ $$    $$ |$$ |
$$$$$$$/   $$$$$$/  $$/          $$$$/   $$$$$$$/ $$/ 
$$ |                                                  
$$ |                                                  
$$/                                                                   
    """

    def compose(self):
        lines = self.TITLE.splitlines(keepends=True)
        text = Text.assemble(*zip(lines, self.COLOURS))

        yield Static(text, classes="title")
        yield Rule()
        yield Markdown(self.WELCOME_MD, id="welcome-msg")