import ttkbootstrap as ttk

STYLE_COUNTER = 0


def stylize_btn(base_style: str = '', font: str = "Helvetica", font_size: int = 18) -> str:
    """
    Stylize your button on top of base styles\n
    Currently supports stylizing font and font size only
    """
    global STYLE_COUNTER
    STYLE_COUNTER += 1

    # Unique name for each style
    stylename: str = "style" + str(STYLE_COUNTER) + "."

    # Insert the built-in styles provided for base re-use; if provided
    if base_style != "":
        stylename += base_style + "."

    # Finalize style by the name of the widget to apply this style to
    stylename += "TButton"

    # Add style to styles
    ttk.Style().configure(
        stylename,
        font=(font, font_size)
    )
    print(stylename)
    return stylename
