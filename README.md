Notifies when new chapters of the Re:Zero web novel, Kaguya-sama manga, and Oshi No Ko manga are translated.

Checks every 10 seconds.

I scrape the data from [WitchCultTranslation](https://witchculttranslation.com/) for Re:zero and [Guya.Moe](https://guya.moe) for Kaguya-sama and Oshi No Ko.

I use [pysaucenao](https://github.com/FujiMakoto/pysaucenao) for reverse image searching.

[Here's the invite link](https://discord.com/api/oauth2/authorize?client_id=834692619392385074&permissions=2148002886&scope=bot).

## Commands

- `r.help cmd` (sends detailed information about the command or just general information if no argument is passed)
- `r.add_channel series` (adds the text channel to the list that will receive notifications), aliases: `r.add`
- `r.remove_channel series` (remove the text channel from the list that will receive notifications), aliases: `r.remove`
- `r.latest_chapter` (informs of the latest translated chapter), aliases: `r.chp`, `r.latest`, `r.last`
- `r.avatar member` (shows a member's avatar or the op's if no argument is passed)
- `r.say message` (make the bot say something)
- `r.clean n` (deletes the last n messages, needs admin permissions), aliases: `r.clear`
- `r.kick member` (kicks a member, needs kick permission), aliases: `r.yeet`, `r.yeeto`
- `r.ban member` (bans a member, needs ban permission)
- `r.unban member` (unbans a member, needs admin permissions)
- `r.remind time unit reason` (reminds the user after 'time' 'unit's (ex. 5 seconds) for 'reason' (not required), d: day(s), h: hour(s), m: minute(s), s: second(s))
- `r.roll x` (rolls a random number between 1 and x(100 if no argument is passed))
- `r.flip` (sends a flip image)
- `r.pout` (sends a pout gif from tenor api)
- `r.pat member` (pat a member or yourself if you want)
- `r.smug` (sends a smug gif from tenor api)
- `r.coinflip h t` (flip a coin h and t are not required), aliases: `r.coin`
- `r.rps choice` (play rock-paper-scissors with Betty)
- `r.reverse_image_search url` (search the image you want for the source), aliases: `r.ris`, `r.sauce`, `r.source`
