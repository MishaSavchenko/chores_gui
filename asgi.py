from main import main
from nicegui import ui


@ui.page('/')
def main_page() -> None:
    main()


ui.run(port=5129)
