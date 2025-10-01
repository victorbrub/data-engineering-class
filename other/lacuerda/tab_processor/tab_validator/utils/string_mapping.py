INTRO = "INTRO:"
CORO = "CORO:"
MAPPING = {
    # Remove
    # Regex
    # Apply with re.IGNORECASE flag
    r"^intro[^ ]*": INTRO,
    r"^\[intro\][^ ]*": INTRO,
    r"^.*intro[\:\n]": INTRO,
    r"^.*introducci[oó]n[\:\n]": INTRO,
    r"^nota:.*\n": "",
    r"^www\..*\n": "",
    r"^[ \n]hola*\n": "",
    r"^.*\n[\-\_]*\n": "",
    r"^.*\n[\-\_]*\n[\-\_]*\n": "",
    r"saludos.*$": "",
    r"nota.*$": "",
    r"letra.*": "",
    r"[\*]*.*[\*]": "",
    r"\n[ ]*[0-9]\)": "",
    r"\n.*CEJILLA[^\n]": "",
    r"estrofa": "",
}
