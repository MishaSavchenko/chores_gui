from datetime import datetime, timedelta
import yaml
from deepdiff import DeepDiff
from copy import deepcopy
from nicegui import ui


def main():
    dark = ui.dark_mode()
    dark.enable()
    ui.label('Switch mode:')
    ui.button('Dark', on_click=dark.enable)
    ui.button('Light', on_click=dark.disable)

    f = './chores.yaml'
    with open(f, 'r') as content:
        chores = yaml.load(content, Loader=yaml.SafeLoader)

    ani_kay = ui.image('kay.svg')
    ani_kay.set_visibility(False)
    ani_misha = ui.image('misha.svg').style('width: 50%')
    ani_misha.set_visibility(False)

    def inject_input(e):

        if e.value == "Kay":
            with ui.teleport(ani_kay):
                ani_kay.set_visibility(True)
                ani_misha.set_visibility(False)
        elif e.value == "Misha":
            with ui.teleport(ani_misha):
                ani_misha.set_visibility(True)
                ani_kay.set_visibility(False)

    diff_history = []
    history_indx = -1

    backward_btn = None
    forward_btn = None

    def time_travel(e):
        print(e)
        global history_indx
        if e.sender == backward_btn:
            history_indx -= 1
            print("backward")
            print(history_indx & len(diff_history))
            pass
        elif e.sender == forward_btn:
            print("forward")
            pass
        else:
            print("FUCK")

    with ui.row():
        user_toggle = ui.toggle(
            ["Kay", "Misha"], value="Misha", on_change=inject_input)

        with ui.button_group():
            backward_btn = ui.button('<-', on_click=time_travel)
            forward_btn = ui.button('->', on_click=time_travel)

    frequency_dict = {"weekly": timedelta(weeks=1),
                      "monthly": timedelta(weeks=4),
                      #   "per-need": timedelta(days=4),
                      "quarterly": timedelta(weeks=12),
                      "semi-weekly": timedelta(days=4),
                      "semi-monthly": timedelta(days=15),
                      }

    for indx, chore in enumerate(chores["chores"]):
        chore["indx"] = indx
        chore["last_date"] = datetime(2023, 5, 4, 0, 0).strftime('%m/%d/%Y')
        chore["last_person"] = ":("

    def update_row_date(row):
        try:
            next_date = datetime.strptime(row["last_date"], '%m/%d/%Y').date() + \
                frequency_dict[row["frequency"]]
            row["next_date"] = next_date.strftime('%m/%d/%Y')
        except KeyError:
            row["next_date"] = r"¯\_(ツ)_/¯"

    def table_selection(sel):

        curr_dict = deepcopy(chores)

        curr_datetime = datetime.today().strftime('%m/%d/%Y')
        indx = sel.selection[0]["indx"]

        chores["chores"][indx]["last_date"] = curr_datetime
        update_row_date(chores["chores"][indx])
        chores["chores"][indx]["last_person"] = user_toggle.value
        sel.sender.update_rows(chores["chores"])

        new_dict = deepcopy(chores)
        diff_history.append(new_dict)
        # diff = DeepDiff(curr_dict, new_dict)
        # diff_history.append(diff)

    table = ui.table(
        columns=[{'name': 'Chore', 'label': 'Chore', 'field': 'name'},
                 {'name': 'Area', 'label': 'Area', 'field': 'area'},
                 {'name': 'Frequency', 'label': 'Frequency', 'field': 'frequency'},
                 {'name': ' ', 'label': ' ', 'field': ' '},
                 {'name': 'last_date', 'label': 'Last Date', 'field': 'last_date'},
                 {'name': 'next_date', 'label': 'Next Date', 'field': 'next_date'},
                 {'name': 'last_person', 'label': 'Last Person', 'field': 'last_person'}
                 ],
        rows=chores["chores"],
        row_key="chore",
        selection="single",
        on_select=table_selection,
    )
    with table.add_slot('body-cell-next_date'):
        with table.cell('next_date') as cell:
            ui.badge().props('''
                            :color=" Date.parse(props.value) < Date.now() ? 'red' : 'green'"
                            :label="props.value"
                            ''')

    # ui.run()


if __name__ in ('__main__', '__mp_main__'):
    main()
    ui.run(port=5000)
