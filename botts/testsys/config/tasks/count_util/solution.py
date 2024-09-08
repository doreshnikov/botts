def count_util(text: str, flags: str | None = None) -> dict[str, int]:
    """
    :param text: text to count entities
    :param flags: flags in command-like format - can be:
        * -m stands for counting characters
        * -l stands for counting lines
        * -L stands for getting length of the longest line
        * -w stands for counting words
    More than one flag can be passed at the same time, for example:
        * "-l -m"
        * "-lLw"
    Ommiting flags or passing empty string is equivalent to "-mlLw"
    :return: mapping from string keys to corresponding counter, where
    keys are selected according to the received flags:
        * "chars" - amount of characters
        * "lines" - amount of lines
        * "longest_line" - the longest line length
        * "words" - amount of words
    """
    if flags is None or flags == "":
        flags = "-mlLw"

    result = {}
    if "m" in flags:
        result["chars"] = len(text)
    if "l" in flags:
        result["lines"] = text.count("\n")
    if "L" in flags:
        result["longest_line"] = max(len(line) for line in text.split("\n"))
    if "w" in flags:
        result["words"] = len(text.split())

    return result
