from textual.screen import ModalScreen
from textual.widgets import Label, LoadingIndicator
from textual.containers import Vertical

import subprocess, sys


class UpdateScreen(ModalScreen):
    DEFAULT_CSS = """
    UpdateScreen {
        align: center middle;

        Label {
            width: 100%;
            text-align: center;
        }

        Vertical {
            max-width: 50%;
            max-height: 50%;
            border: panel $primary;
            align: center middle;
        }

        LoadingIndicator {
            height: 1;
        }
    }
    """

    def compose(self):
        with Vertical() as window:
            window.border_title = "=== Portal is Updating... ==="
            yield Label("[b u]Checking for updates...[/b u]", id="title")
            yield Label("[dim]This will only take a moment!\nPortal will restart after the updates are complete[/dim]")
            yield LoadingIndicator()

    def on_mount(self):
        title = self.query_one("#title")

        if self.check_for_updates()[0] == True:
            title.update("[b u]Portal is updating...[/b u]")
            self.update()
        else:
            self.dismiss()

    def update(self):
        origin = self.repo.remotes.origin
        origin.pull()

        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)

    def has_unstaged_changes(self):
        # Files modified but not yet staged
        unstaged = self.repo.index.diff(None)

        # Untracked (new) files
        untracked = self.repo.untracked_files

        has_changes = bool(unstaged) or bool(untracked)

        return has_changes, unstaged, untracked

    def check_for_updates(self):
        """Checks repo for updates.

        Returns:
            bool: Is the current branch behind?
            int: How many commits is the current branch behind?
        """
        try:
            has_changes, _, _ = self.has_unstaged_changes() 
        except:
            return False, 0

        current_branch = self.repo.active_branch
        self.repo.remotes.origin.fetch()

        behind_count = sum(1 for c in self.repo.iter_commits(f"{current_branch}..origin/{current_branch}"))
    
        return behind_count > 0, behind_count