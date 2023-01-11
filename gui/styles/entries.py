import ttkbootstrap as ttk

STYLE_COUNTER = 0


def stylize_entry(base_style: str = '', background: str = 'dark'):
    """
    Stylize your entry on top of base styles\n
    NON-FUNCTIONAL NON-FUNCTIONAL NON-FUNCTIONAL\n
    Current supports setting background only\n
    NON-FUNCTIONAL NON-FUNCTIONAL NON-FUNCTIONAL
    """
    global STYLE_COUNTER
    STYLE_COUNTER += 1

    # Unique name for each style
    stylename: str = "style" + str(STYLE_COUNTER) + "."

    # Insert the built-in styles provided for base re-use; if provided
    if base_style != "":
        stylename += base_style + "."

    # Finalize style by the name of the widget to apply this style to
    stylename += "TEntry"

    # Add style to styles
    ttk.Style().configure(
        stylename,
        fieldbackground=background
    )
    print(stylename)
    return stylename
