def tokenize_command(line):
    """

    Source: https://github.com/mottosso/maya-scenefile-parser/

    :param line: str
    :return:
    """
    command, _, line = line.partition(" ")
    command = command.lstrip()

    args = list()
    while True:
        line = line.strip()

        if not line:
            break

        # handle quotation marks in string
        if line[0] in ['\"', "\'"]:
            string_delim = line[0]
            escaped = False
            string_end = len(line)

            # find the closing quote as string end
            for i in range(1, len(line)):
                if not escaped and line[i] == string_delim:
                    string_end = i
                    break
                elif not escaped and line[i] == "\\":
                    escaped = True
                else:
                    escaped = False

            arg, line = line[1:string_end], line[string_end+1:]

        else:
            arg, _, line = line.partition(" ")

        args.append(arg)

    return command, args
