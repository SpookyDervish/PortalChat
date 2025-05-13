from textual.screen import ModalScreen
from textual.widgets import Static, DataTable, LoadingIndicator, Button
from textual.containers import Vertical
from textual import work, on

from ui.widgets.sidebar_icon import Icon
from server.scan import scan_network, get_subnet_network, get_subnet


class AddServer(ModalScreen):
    DEFAULT_CSS = """
    AddServer {
        align: center middle;

        #add-serv-win {
            align-horizontal: center;
            border: tab $primary;
            width: 50%;
            height: 65%;
            border-title-align: center;
            padding: 1;

            Rule {
                color: $background-lighten-3;
            }

            #btm-sect {
                dock: bottom;
                background: $boost;
                border: tall $background-lighten-1;
                height: 5;
                margin-top: 1;

                Button {
                    margin-left: 1;
                }
            }

            Static {
                margin-top: 1;
                width: 100%;
                text-align: center;
            }

            LoadingIndicator {
                height: 1;
                margin-top: 1;
            }
        }
    }
    """
    
    def on_mount(self):
        self.selected_server = None
        table: DataTable = self.query_one("#serv-table")
        table.add_columns("Title", "# Online", "IP")
        self.find_servers_worker = self.find_servers(table)

    @work(thread=True)
    def find_servers(self, table: DataTable):
        local_ip, netmash = get_subnet()
        for server in scan_network(get_subnet_network(local_ip, netmash)):
            # we minus 1 from the online count otherwise it includes ourselves
            table.add_row(server["data"]["title"], server["data"]["online"]-1, server["ip"])

        # remove loading text when done searching for servers
        self.query_one("#loading1").remove()
        self.query_one("#loading2").remove()

    @on(DataTable.RowHighlighted)
    def select_server(self, event: DataTable.RowHighlighted):
        join_server_btn = self.query_one("#join-serv")

        table = event.data_table
        self.selected_server = table.get_row(event.row_key)
        join_server_btn.disabled = False

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed):
        if event.button.id == "join-serv" and self.selected_server is not None:
            self.dismiss()

            sidebar = self.app.query_one("#sidebar")
            icons = sidebar.query_one("#icons")

            icons.mount(Icon(self.selected_server, True))

    def on_key(self, event):
        if event.key == "escape":
            if self.find_servers_worker:
                self.find_servers_worker.cancel()
            self.dismiss()

    def compose(self):
        with Vertical(id="add-serv-win") as window:
            window.border_title = "=== Add a Server ==="

            yield DataTable(id="serv-table", cursor_type="row")

            yield Static("[dim]Searching for servers...[/dim]", id="loading1")
            yield LoadingIndicator(id="loading2")

            with Vertical(id="btm-sect"):
                yield Button("Join", disabled=True, tooltip="Join the selected server", variant="success", id="join-serv")