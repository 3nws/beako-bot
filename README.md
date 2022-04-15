Notifies text channels when new chapters of the series they follow are translated on [MangaDex](https://mangadex.org). For Re:Zero web novel, Grand Blue Dreaming manga, Kaguya-sama manga, and Oshi No Ko manga I use beautifulsoup because I like them on specific websites mentioned below.

Checks every 60 seconds.

I scrape the data from [WitchCultTranslation](https://witchculttranslation.com/) for Re:zero, [MangaReader](https://mangareader.to) for Grand Blue, and [Guya.Moe](https://guya.moe) for Kaguya-sama and Oshi No Ko.

Now also supports (hopefully) any series on [MangaDex](https://mangadex.org) with a search function and everything. Pretty cool [API](https://api.mangadex.org/swagger.html#/) they got there. Nice.

I use [pysaucenao](https://github.com/FujiMakoto/pysaucenao) for reverse image searching.

[Here's the invite link](https://discord.com/api/oauth2/authorize?client_id=834692619392385074&permissions=2148002822&scope=bot).

## Series tracking and database action commands and the help command

- `r.help cmd` (sends detailed information about the command or just general information if no argument is passed)
- `r.add_channel series` (adds the text channel to the list that will receive notifications, if the series is not one of the four mentioned above it will search on mangadex and add them instead), alias: `r.add`
- `r.remove_channel series` (remove the text channel from the list that will receive notifications, if no series argument is passed it will show the series followed on mangadex by the text channel), aliases: `r.remove`
- `r.manga series` (gives information about the given manga series), alias: `r.info`
- `r.latest_chapter series` (informs of the latest translated chapter of given series), aliases: `r.chp`, `r.latest`, `r.last`
- `r.following` (sends a message with the list of series a channel is following), aliases: `r.follow`, `r.fol`, `r.watching`, `r.follows`
- `r.flip` (sends a flip image)

## Admin commands

- `r.toggle command` (enables/disables commands)
- `r.terminate` (), alias: `r.kill`
- `r.servers` (prints the servers the bot is in to the logs)
- `r.purge member` (deletes all the messages of the given member from the current text channel, needs admin permissions), alias: `r.cleanse`
- `r.clean n direction msg_id` (deletes the last n messages starting from message with the id msg_id (not required) in the direction you specify, needs admin permissions), alias: `r.clear`
- `r.kick member` (kicks a member, needs kick permission), aliases: `r.yeet`, `r.yeeto`
- `r.ban member` (bans a member, needs ban permission)
- `r.unban member` (unbans a member, needs admin permissions)

## Util commands

- `r.poll choice1 choice2 question` (creates a poll with the choices and the question, polls have a 3 minute timer before they are finished)
- `r.reverse_image_search url` (search the image you want for the source), aliases: `r.ris`, `r.sauce`, `r.source`
- `r.avatar member` (shows a member's avatar or the op's if no argument is passed)
- `r.banner member` (shows a member's banner or the op's if no argument is passed)
- `r.series` (sends a list of series available for tracking)

## osu! commands

- `r.osu player` (sends information about the player), aliases: `r.u`, `r.user`
- `r.osutop player` (sends player's top plays), aliases: `r.top`, `r.best`
- `r.recent player` (sends player's most recent plays), aliases: `r.rs`, `r.rc`

## Fun commands

- `r.coinflip h t` (flip a coin h and t are not required), alias: `r.coin`
- `r.rps choice` (play rock-paper-scissors with Betty)
- `r.roll x` (rolls a random number between 1 and x(100 if no argument is passed))
- `r.say message` (make the bot say something)

## Gif commands

- `r.pout` (sends a pout gif from tenor api)
- `r.pat member` (pat a member or yourself if you want)
- `r.hug member` (hug a member or yourself if you so need)
- `r.smug` (sends a smug gif from tenor api)

## Timer commands

- `r.alarm time reason` (sets an alarm for you and pings you at that time, only works in the same day though, at least for now)
- `r.remind time unit reason` (reminds the user after 'time' 'unit's (ex. 5 seconds) for 'reason' (not required), d: day(s), h: hour(s), m: minute(s), s: second(s))

## Tasks

- `change_avatar()` (changes avatar everyday, selecting randomly from db)
- `check_chapter()` (checks the latest chapters of the followed series every minute and notifies)
- `filter_channels()` (filters out the channels that no longer exists from the db)

### TODOS

- Add more osu! functionality
- Make the results prettier, they look awful