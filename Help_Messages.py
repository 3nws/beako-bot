messages = {
    '': "```Prefix is 'r.', in fact!\
                 \nTo get help and to learn aliases for a specific command use r.help <command> (you can also use an alias), I suppose!\
                 \nAvailable commands are:\
                 \n-add_channel (alias: add)\
                 \n-remove_channel (alias: remove)\
                 \n-manga (alias: info)\
                 \n-latest_chapter (aliases: latest, last, chp)\
                 \n-avatar\
                 \n-banner\
                 \n-following (aliases: follow, fol, watching, follows)\
                 \n-say\
                 \n-clean (alias: clear)\
                 \n-purge (alias: cleanse)\
                 \n-kick (aliases: yeet, yeeto)\
                 \n-ban\
                 \n-unban\
                 \n-osu (aliases: u, user)\
                 \n-osutop (aliases: top, best)\
                 \n-recent (aliases: rs, rc)\
                 \n-alarm\
                 \n-remind (aliases: remindme, remind_me)\
                 \n-poll\
                 \n-roll\
                 \n-flip\
                 \n-pout\
                 \n-hug\
                 \n-pat\
                 \n-smug\
                 \n-series\
                 \n-coinflip (alias: coin)\
                 \n-reverse_image_search (aliases: ris, sauce, source)\
                 \n-rps, in fact!```",

        'avatar': "```Betty will send a member's(author's if no member is passed) avatar to the text channel, in fact!```",

        'server_avatar': "```Betty will send a member's(author's if no member is passed) server avatar to the text channel, in fact!```",

        'banner': "```Betty will send a member's(author's if no member is passed) banner to the text channel, in fact!```",

        'add_channel': "```Betty will add the text channel to the list of channels that will receive notifications of the preferred series, I suppose!```",

        'remove_channel': "```Betty will remove the text channel from the list of channels that will receive notifications of the preferred series, I suppose! No need to name any series if its on MangaDex, in fact!```",

        'manga': "```Betty will give information about the manga you want, in fact!```",

        'following': "```Betty will send a list of series the text channel is following for, I suppose!```",

        'say': "```Betty will repeat what you say, I suppose!```",

        'clean': "```Betty will clean up the text channel by the specified amount of messages, in fact! If you like you can specify which message it will start from by passing its ID and a direction, I suppose!```",

        'purge': "```Betty will delete all messages of the given member from the current text channel, I suppose!```",

        'kick': "```Betty will use wind magic to kick a member, I suppose!```",

        'ban': "```Betty will use yin magic to ban a member, I suppose!```",

        'unban': "```Betty will forgive a member and remove their ban, I suppose!```",

        'osu': "```Betty will give information about a player, I suppose!\
                    \nThe format for this is 'osu player', in fact!```",

        'osutop': "```Betty will tell you a player's top scores, I suppose!\
                    \nThe format for this is 'osutop player', in fact!```",

        'recent': "```Betty will tell you a player's 5 most recent plays, I suppose!\
                    \nThe format for this is 'recent player', in fact!```",

        'alarm': "```Betty will set an alarm for you, I suppose!\
                   \nThe format for this is 'alarm time reason'\
                   \nTime needs to be in this format: '<hour>:<minute>' in 24 hour format of course, '.' can be used instead of ':'\
                   \n(I will only remind you if your alarm is on the same day, I suppose!)```",

        'remind': "```Betty will remind the author after specified time by pinging them, I suppose!\
                    \nThe format for this is 'remind time unit reason'\
                    \n(The unit can be concatenated with remind such as remind 5m coffee, s: seconds, m: minutes, h: hours, d: days, ex. remind 5 m coffee), in fact!```",

        'poll': "```Betty will create a poll for the server, I suppose!\
                    \nThe format for this is 'poll choice1 choice2 question'\
                    \nBetty will return the results in three minutes, in fact!```",

        'roll': "```Betty will roll a number for the author between 0 and the specified number(100 if not), I suppose!```",

        'flip': "```Betty doesn't want to talk about it, in fact!```",

        'pout': "```Betty will send pout gifs from tenor gif, I suppose!```",

        'hug': "```Betty will send hugging gifs from tenor gif, I suppose!```",

        'pat': "```Pat a member or yourself(how pathetic, in fact!).```",

        'smug': "```Betty will send smug gifs from tenor gif, I suppose!```",

        'series': "```Betty will tell you the series available in the database, I suppose!```",

        'coinflip': "```Betty will flip a coin, I suppose!\
                      \nThe format for this is 'coinflip for_heads(not required) for_tails(not required)' (ex. coinflip lol valo), in fact!```",

        'latest_chapter': "```Betty will tell you what the latest translated chapter for the given series is, I suppose!\
                            \nIf it is from MangaDex, I might even send a reader, in fact!```",

        'rps': "```Betty will play rock-paper-scissors with you, I suppose! Rejoice, in fact!\
                 \nThe format for this is 'rps choice' (ex. rps rock), in fact!```",

        'reverse_image_search': "```Betty will reverse search for the image you want, I suppose!\
                                  \nThe format for this is 'reverse_image_search url', in fact!```",

}

aliases = {
    'add': 'add_channel',
    'remove': 'remove_channel',
    'clear': 'clean',
    'yeet': 'kick',
    'yeeto': 'kick',
    'remindme': 'remind',
    'remind_me': 'remind',
    'coin': 'coinflip',
    'latest': 'latest_chapter',
    'last': 'latest_chapter',
    'chp': 'latest_chapter',
    'ris': 'reverse_image_search',
    'sauce': 'reverse_image_search',
    'source': 'reverse_image_search',
    'watching': 'following',
    'follow': 'following',
    'fol': 'following',
    'follows': 'following',
    'cleanse': 'purge',
    'info': 'manga',
    'user': 'osu',
    'u': 'osu',
    'best': 'osutop',
    'top': 'osutop',
    'rs': 'recent',
    'rc': 'recent',
    'savatar': 'server_avatar'
}
