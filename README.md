Notifies text channels when new chapters of the series they follow are translated on [MangaDex](https://mangadex.org). For Re:Zero web novel, Grand Blue Dreaming manga, Kaguya-sama manga, and Oshi No Ko manga I use beautifulsoup because I like them on specific websites mentioned below.

Checks every 60 seconds.

I scrape the data from [WitchCultTranslation](https://witchculttranslation.com/) for Re:zero, [MangaReader](https://mangareader.to) for Grand Blue, and [Guya.Moe](https://guya.moe) for Kaguya-sama and Oshi No Ko.

Now also supports (hopefully) any series on [MangaDex](https://mangadex.org) with a search function and a reader. Pretty cool [API](https://api.mangadex.org/swagger.html#/) they got there. Nice.

I use [pysaucenao](https://github.com/FujiMakoto/pysaucenao) for reverse image searching.

## Series tracking and database action commands and the help command

- `/help cmd` (sends detailed information about the command or just general information if no argument is passed)
- `/add series` (adds the text channel to the list that will receive notifications, if the series is not one of the four mentioned above it will search on mangadex and add them instead)
- `/remove series` (remove the text channel from the list that will receive notifications, if no series argument is passed it will show the series followed on mangadex by the text channel)
- `/manga series` (gives information about the given manga series)
- `/last series` (informs of the latest translated chapter of given series, sends a reader for MangaDex)
- `/following` (sends a message with the list of series a channel is following)
- `/flip` (sends a flip image)

## Admin commands

- `r.toggle command` (enables/disables commands)
- `r.terminate` alias: `r.kill`
- `/servers` (prints the servers the bot is in to the logs)
- `/purge member` (deletes all the messages of the given member from the current text channel, needs admin permissions)
- `/clean n direction msg_id` (deletes the last n messages starting from message with the id msg_id (not required) in the direction you specify, needs admin permissions)
- `/kick member` (kicks a member, needs kick permission)
- `/ban member` (bans a member, needs ban permission)
- `/unban member` (unbans a member, needs admin permissions)

## Util commands

- `/poll choice1 choice2 question` (creates a poll with the choices and the question, polls have a 3 minute timer before they are finished)
- `/sauce url` (search the image you want for the source)
- `/avatar member` (shows a member's avatar or the op's if no argument is passed)
- `/savatar member` (shows a member's avatar or the op's if no argument is passed)
- `/banner member` (shows a member's banner or the op's if no argument is passed)
- `/series` (sends a list of series available for tracking)

## osu! commands

- `/osu player` (sends information about the player)
- `/best player` (sends player's top plays)
- `/recent player` (sends player's most recent plays)

## Fun commands

- `/coin h t` (flip a coin h and t are not required)
- `/rps choice` (play rock-paper-scissors with Betty)
- `/roll x` (rolls a random number between 1 and x(100 if no argument is passed))
- `/say message` (make the bot say something)

## Gif commands

- `/pout` (sends a pout gif from tenor api)
- `/pat member` (pat a member or yourself if you want)
- `/hug member` (hug a member or yourself if you so need)
- `/smug` (sends a smug gif from tenor api)

## Timer commands

- `/alarm time reason` (sets an alarm for you and pings you at that time, only works in the same day though, at least for now)
- `/remind time unit reason` (reminds the user after 'time' 'unit's (ex. 5 seconds) for 'reason' (not required), d: day(s), h: hour(s), m: minute(s), s: second(s))

## Warframe commands

- `/item order_type item_name` (send info about an item as well as several orders of given type with their /w message templates)
- 
## Tasks

- `change_avatar()` (changes avatar everyday, selecting randomly from db)
- `check_chapter()` (checks the latest chapters of the followed series every minute and notifies)
- `filter_channels()` (filters out the channels that no longer exists from the db)


### TODOS

- Add more osu! functionality
- Make the results prettier, they look awful
- Add tracking for animes as well
