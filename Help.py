class Help:
    def __init__(self, cmd):
        self.cmd = cmd
    
    def get_help(self):
        help_message = "No such command, in fact!"
        if self.cmd == "":
            help_message = "```Prefix is 'r.', in fact!\
                            \nTo get help and to learn aliases for a specific command use r.help <command>, I suppose!\
                            \nAvailable commands are:\
                            \n-add_channel\
                            \n-remove_channel\
                            \n-latest_chapter\
                            \n-avatar\
                            \n-say\
                            \n-clean\
                            \n-kick\
                            \n-ban\
                            \n-unban\
                            \n-remind\
                            \n-roll\
                            \n-flip\
                            \n-pout\
                            \n-pat\
                            \n-smug\
                            \n-coinflip\
                            \n-reverse_image_search\
                            \n-rps, in fact!```"                                                                                                                                                              
        elif self.cmd == "avatar":
            help_message = "```Betty will send a member's(author's if no member is passed) avatar image to the text channel, in fact!```"
        elif self.cmd == "add_channel":
            help_message = "```Betty will add the text channel to the list of channels that will receive notifications of the preferred series, I suppose!\
                            \nAn alias for this is 'add', in fact!```"
        elif self.cmd == "remove_channel":
            help_message = "```Betty will remove the text channel from the list of channels that will receiv notifications of the preferred series, I suppose!\
                            \nAn alias for this is 'remove', in fact!```"
        elif self.cmd == "say":
            help_message = "```Betty will repeat what you say, I suppose!```"
        elif self.cmd == "clean":
            help_message = "```Betty will clean up the text channel by the specified amount of messages, in fact!\
                            \nAn alias for this is 'clear', in fact!```"
        elif self.cmd == "kick":
            help_message = "```Betty will use wind magic to kick a member, I suppose!\
                            \nAliases for this are 'yeet' and 'yeeto', in fact!```"
        elif self.cmd == "ban":
            help_message = "```Betty will use yin magic to ban a member, I suppose!```"
        elif self.cmd == "unban":
            help_message = "```Betty will forgive a member and remove their ban, I suppose!```"
        elif self.cmd == "remind":
            help_message = "```Betty will remind the author after specified time by pinging them, I suppose!\
                            \nThe format for this is 'remind time unit reason'\
                            \n(The unit can be concatenated with remind such as remind 5m coffee, s: seconds, m: minutes, h: hours, d: days, ex. remind 5 m coffee), in fact!```"
        elif self.cmd == "roll":
            help_message = "```Betty will roll a number for the author between 0 and the specified number(100 if not), I suppose!```"
        elif self.cmd == "flip":
            help_message = "```Betty doesn't want to talk about it, in fact!```"
        elif self.cmd == "pout":
            help_message = "```Betty will send pout gifs from tenor gif, I suppose!```"
        elif self.cmd == "pat":
            help_message = "```Pat a member or yourself(how pathetic, in fact!).```"
        elif self.cmd == "smug":
            help_message = "```Betty will send smug gifs from tenor gif, I suppose!```"
        elif self.cmd == "coinflip":
            help_message = "```Betty will flip a coin, I suppose!\
                            \nAn alias for this is 'coin', in fact!\
                            \nThe format for this is 'coinflip for_heads(not required) for_tails(not required)' (ex. coinflip lol valo), in fact!```"
        elif self.cmd == "latest_chapter":
            help_message = "```Betty will tell you what the latest translated chapter is, I suppose!\
                            \nAliases for this are 'chp', 'latest', and 'last' in fact!```"
        elif self.cmd == "rps":
            help_message = "```Betty will play rock-paper-scissors with you, I suppose! Rejoice, in fact!\
                            \nThe format for this is 'rps choice' (ex. rps rock), in fact!```"
        elif self.cmd == "reverse_image_search":
            help_message = "```Betty will reverse search for the image you want, I suppose!\
                            \nAliases for this are 'ris', 'sauce', and 'source' in fact!\
                            \nThe format for this is 'reverse_image_search url', in fact!```"
        
        return help_message
