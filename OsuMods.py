from typing import List


def num_to_mod(number: int) -> List[str]:
    """This is the way pyttanko does it. (https://github.com/AznStevy/owo/blob/6d7b63494aa4534d93b32a16f03db8ed1dbbb47a/cogs/osu.py#L3211)
    Just as an actual bitwise instead of list.
    Deal with it."""
    number = number
    mod_list: List[str] = []

    if number & 1 << 0:
        mod_list.append("NF")
    if number & 1 << 1:
        mod_list.append("EZ")
    if number & 1 << 3:
        mod_list.append("HD")
    if number & 1 << 4:
        mod_list.append("HR")
    if number & 1 << 5:
        mod_list.append("SD")
    if number & 1 << 9:
        mod_list.append("NC")
    elif number & 1 << 6:
        mod_list.append("DT")
    if number & 1 << 7:
        mod_list.append("RX")
    if number & 1 << 8:
        mod_list.append("HT")
    if number & 1 << 10:
        mod_list.append("FL")
    if number & 1 << 12:
        mod_list.append("SO")
    if number & 1 << 14:
        mod_list.append("PF")
    if number & 1 << 15:
        mod_list.append("4 KEY")
    if number & 1 << 16:
        mod_list.append("5 KEY")
    if number & 1 << 17:
        mod_list.append("6 KEY")
    if number & 1 << 18:
        mod_list.append("7 KEY")
    if number & 1 << 19:
        mod_list.append("8 KEY")
    if number & 1 << 20:
        mod_list.append("FI")
    if number & 1 << 24:
        mod_list.append("9 KEY")
    if number & 1 << 25:
        mod_list.append("10 KEY")
    if number & 1 << 26:
        mod_list.append("1 KEY")
    if number & 1 << 27:
        mod_list.append("3 KEY")
    if number & 1 << 28:
        mod_list.append("2 KEY")

    return mod_list
