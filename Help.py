from Help_Messages import messages
class Help:
    def __init__(self, cmd):
        self.cmd = cmd
    
    def get_help(self):        
        return "No such command, in fact!" if self.cmd not in messages else messages[self.cmd]