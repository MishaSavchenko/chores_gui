from datetime import datetime, timedelta
import yaml
import json
from deepdiff import DeepDiff
from copy import deepcopy
from nicegui import ui, events


class ChoresGui:

    diff_history = []
    history_indx = 0

    chores_filename = "db/chores.json"

    # Buttons
    backward_btn = None
    timestamp_btn = None
    forward_btn = None

    frequency_dict = {"weekly": timedelta(weeks=1),
                      "monthly": timedelta(weeks=4),
                      #   "per-need": timedelta(days=4),
                      "quarterly": timedelta(weeks=12),
                      "semi-weekly": timedelta(days=4),
                      "semi-monthly": timedelta(days=15),
                      }

    def __init__(self, debug=True):
        if debug:
            f = './chores.yaml'
            with open(f, 'r') as content:
                chores_schema = yaml.load(content, Loader=yaml.SafeLoader)

            for indx, chore in enumerate(chores_schema["chores"]):
                chore["indx"] = indx
                chore["last_date"] = datetime(
                    2023, 5, 4, 0, 0).strftime('%m/%d/%Y')
                chore["last_person"] = ":("

            chores_schema["timestamp"] = datetime.now()
            self.diff_history.append(chores_schema)

            self.chores_filename = "db/debug_chores.json"

        else:
            loaded_chores = None
            with open(self.chores_filename, "r") as file:
                loaded_chores = json.load(file)

            self.diff_history.append(loaded_chores)

        ani_kay = ui.image('kay.svg')
        ani_kay.set_visibility(False)
        ani_misha = ui.image('misha.svg').style('width: 50%')
        ani_misha.set_visibility(False)

        self.layout_setup()

    def layout_setup(self):

        dark = ui.dark_mode()
        dark.enable()
        ui.label('Switch mode:')
        ui.button('Dark', on_click=dark.enable)
        ui.button('Light', on_click=dark.disable)

        with ui.row():
            self.user_toggle = ui.toggle(
                ["Kay", "Misha"], value="Misha", on_change=self.inject_input)

            # with ui.button_group():
            #     self.backward_btn = ui.button('<-', on_click=self.time_travel)
            #     self.timestamp_btn = ui.button('Click me!')
            #     self.timestamp_btn.set_text(self.get_chores()["timestamp"])
            #     self.forward_btn = ui.button('->', on_click=self.time_travel)

        self.table = ui.table(
            columns=[{'name': 'Chore', 'label': 'Chore', 'field': 'name'},
                     {'name': 'Area', 'label': 'Area', 'field': 'area'},
                     {'name': 'Frequency', 'label': 'Frequency',
                      'field': 'frequency'},
                     {'name': ' ', 'label': ' ', 'field': ' '},
                     {'name': 'last_date', 'label': 'Last Date',
                      'field': 'last_date'},
                     {'name': 'next_date', 'label': 'Next Date',
                      'field': 'next_date'},
                     {'name': 'last_person', 'label': 'Last Person',
                         'field': 'last_person'}
                     ],
            rows=self.get_chores()["chores"],
            row_key="chore",
            selection="single",
            on_select=self.table_selection,
        )
        with self.table.add_slot('body-cell-next_date'):
            with self.table.cell('next_date') as cell:
                ui.badge().props('''
                                :color=" Date.parse(props.value) < Date.now() ? 'red' : 'green'"
                                :label="props.value"
                                ''')

    def get_chores(self, index: int = None) -> dict:
        if index is None:
            index = len(self.diff_history) - 1

        return self.diff_history[index]

    def inject_input(self, e):

        if e.value == "Kay":
            with ui.teleport(self.ani_kay):
                self.ani_kay.set_visibility(True)
                self.ani_misha.set_visibility(False)
        elif e.value == "Misha":
            with ui.teleport(self.ani_misha):
                self.ani_misha.set_visibility(True)
                self.ani_kay.set_visibility(False)

    def update_row_date(self, row):
        try:
            next_date = datetime.strptime(row["last_date"], '%m/%d/%Y').date() + \
                self.frequency_dict[row["frequency"]]
            row["next_date"] = next_date.strftime('%m/%d/%Y')
        except KeyError:
            row["next_date"] = r"¯\_(ツ)_/¯"

    def table_selection(self, sel):
        curr_datetime = datetime.today().strftime('%m/%d/%Y')
        indx = sel.selection[0]["indx"]

        updated_chores = deepcopy(self.get_chores())

        updated_chores["chores"][indx]["last_date"] = curr_datetime
        self.update_row_date(updated_chores["chores"][indx])
        updated_chores["chores"][indx]["last_person"] = self.user_toggle.value
        sel.sender.update_rows(updated_chores["chores"])

        if updated_chores["chores"] != self.get_chores()["chores"]:
            updated_chores["timestamp"] = datetime.now().timestamp()
            self.diff_history.append(updated_chores)
            # self.time_travel(sel)
            self.save_data()

    def save_data(self):
        with open(self.chores_filename, 'w') as fp:
            json.dump(self.diff_history[-1], fp, indent=4, ensure_ascii=False)

    def time_travel(self, e: events.ClickEventArguments) -> None:
        if e.sender == self.backward_btn:
            self.history_indx = (self.history_indx -
                                 1) % len(self.diff_history)
        elif e.sender == self.forward_btn or e.sender == self.table:
            self.history_indx = (self.history_indx +
                                 1) % len(self.diff_history)

        if self.history_indx == 0:
            self.backward_btn.disable()
        else:
            self.backward_btn.enable()

        if self.history_indx == len(self.diff_history) - 1:
            self.forward_btn.disable()
        else:
            self.forward_btn.enable()

        self.table.update_rows(self.diff_history[self.history_indx]["chores"])
        self.timestamp_btn.set_text(
            self.diff_history[self.history_indx]["timestamp"])


def main():
    ChoresGui(debug=False)


if __name__ in ('__main__', '__mp_main__'):
    main()
    ui.run(port=5000)
