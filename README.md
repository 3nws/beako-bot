Notifies when a new chapter of the Re:Zero web novel is translated.

Checks every 10 seconds.

I scrape the data from [WitchCultTranslation](https://witchculttranslation.com/).

[Here's the invite link](https://discord.com/api/oauth2/authorize?client_id=834692619392385074&permissions=2148002886&scope=bot).

## Commands

- r.avatar x (shows a user's avatar or the op's if no argument is passed)
- r.add_channel (adds the text channel to the list that will receive notifications)
- r.remove_channel (remove the text channel from the list that will receive notifications)
- r.say x (make the bot say something)
- r.clean x (deletes the last x messages, needs admin permissions)
- r.kick x (kicks the user x, needs kick permission)
- r.ban x (bans the user x, needs ban permission)
- r.unban x (unbans the user x, needs admin permissions)
- r.remind x y z (reminds the user after x y's (ex. 5 seconds) for z (not required), d: day(s), h: hour(s), m: minute(s), s: second(s))
- r.roll x (rolls a random number between 1 and x(100 if no argument is passed))
- r.flip (sends a flip image)
- r.pout (sends a pout gif from tenor api)
- r.pat x (pat another user or yourself if you want)

### TODO

- remove channel_id from db when a channel is deleted.
