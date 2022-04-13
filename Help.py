from Help_Messages import messages, aliases


class Help:
    def __init__(self, cmd):
        self.cmd = aliases[cmd] if cmd in aliases else cmd

    def get_help(self):
        return "No such command, in fact!" if self.cmd not in messages else messages[self.cmd]
