import logging
import os
from itertools import islice

import flet
from flet import (
    Column,
    Container,
    GridView,
    Icon,
    IconButton,
    Page,
    Row,
    SnackBar,
    Text,
    TextButton,
    TextField,
    UserControl,
    alignment,
    colors,
    cupertino_icons,
)

# logging.basicConfig(level=logging.INFO)

os.environ["FLET_WS_MAX_MESSAGE_SIZE"] = "8000000"


class IconCupertinoBrowser(UserControl):
    def __init__(self, expand=False, height=500):
        super().__init__()
        if expand:
            self.expand = expand
        else:
            self.height = height

    def build(self):
        def batches(iterable, batch_size):
            iterator = iter(iterable)
            while batch := list(islice(iterator, batch_size)):
                yield batch

        # fetch all icon constants from icons.py module
        icons_list = []
        list_started = False
        # loop through cupertino icons
        for key, value in vars(cupertino_icons).items():
            # use top-most from flet/sdk/python/packages/flet-core/src/flet_core/cupertino_icons.py
            if key == "LEFT_CHEVRON":
                list_started = True
            if list_started and isinstance(value, str):
                icons_list.append(value)

        search_txt = TextField(
            expand=1,
            hint_text="Enter keyword and press search button. To view all icons enter *",
            autofocus=True,
            on_submit=lambda e: display_icons(e.control.value),
        )

        def search_click(e):
            display_icons(search_txt.value)

        search_query = Row(
            [search_txt, IconButton(icon=cupertino_icons.SEARCH, on_click=search_click)]
        )

        search_results = GridView(
            expand=1,
            runs_count=10,
            max_extent=150,
            spacing=5,
            run_spacing=5,
            child_aspect_ratio=1,
        )
        status_bar = Text()

        def copy_to_clipboard(e):
            icon_key = e.control.data
            print("Copy to clipboard:", icon_key)
            self.page.set_clipboard(e.control.data)
            self.page.show_snack_bar(SnackBar(Text(f"Copied {icon_key}"), open=True))

        def search_icons(search_term: str):
            # switch variable to allow empty search, which shows all icons
            all_icons = 0
            for icon_name in icons_list:
                if all_icons == 1 or search_term != "":
                    # match search to query
                    if search_term != "" and search_term in icon_name:
                        all_icons = 0
                        yield icon_name
                    # turn on switch, empty search, and yield to not skip 1st icon
                    elif search_term == "*":
                        all_icons = 1
                        search_term = ""
                        yield icon_name
                    # all_icons is 1, which allows for empty search, which shows all
                    elif search_term == "" and all_icons == 1:
                        yield icon_name
                    else:
                        all_icons = 0

        def display_icons(search_term: str):

            # clean search results
            search_query.disabled = True
            self.update()

            search_results.clean()

            for batch in batches(search_icons(search_term.lower()), 200):
                for icon_name in batch:
                    # HOT GLUE - primitive text in replace to diplay & copy correctly.
                    icon_key = f"cupertino_icons.{icon_name.upper()}".replace("cupertino_".upper(), "")
                    search_results.controls.append(
                        TextButton(
                            content=Container(
                                content=Column(
                                    [
                                        Icon(name=icon_name, size=30),
                                        Text(
                                            # HOT GLUE - primitive text in replace to diplay & copy correctly.
                                            value=f"{icon_name}".replace("cupertino_", ""),
                                            size=12,
                                            width=100,
                                            no_wrap=True,
                                            text_align="center",
                                            color=colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    spacing=5,
                                    alignment="center",
                                    horizontal_alignment="center",
                                ),
                                alignment=alignment.center,
                            ),
                            tooltip=f"{icon_key}\nClick to copy to a clipboard",
                            on_click=copy_to_clipboard,
                            data=icon_key,
                        )
                    )
                status_bar.value = f"Icons found: {len(search_results.controls)}"
                self.update()

            if len(search_results.controls) == 0:
                self.page.show_snack_bar(SnackBar(Text("No icons found"), open=True))
            search_query.disabled = False
            self.update()

        return Column(
            [
                search_query,
                search_results,
                status_bar,
            ],
            expand=True,
        )


def main(page: Page):
    page.title = "Flet cupertino icons browser"
    page.add(IconCupertinoBrowser(expand=True))


flet.app(target=main)
