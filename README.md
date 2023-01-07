# Beako-bot

Notifies text channels when new chapters of the series they follow are translated on [MangaDex](https://mangadex.org). For Re:Zero web novel, Grand Blue Dreaming manga, Kaguya-sama manga, and Oshi No Ko manga I use beautifulsoup because I like them on specific websites mentioned below.

Checks every 15 minutes.

I scrape the data from [WitchCultTranslation](https://witchculttranslation.com/) for Re:zero, [MangaReader](https://mangareader.to) for Grand Blue, and [Guya.Moe](https://guya.moe) for Kaguya-sama and Oshi No Ko.

Now also supports (hopefully) any series on [MangaDex](https://mangadex.org) with a search function and a reader. Pretty cool [API](https://api.mangadex.org/swagger.html#/) they got there. Nice.

It also has some osu! and WarframeMarket features, more info below.

I use [pysaucenao](https://github.com/FujiMakoto/pysaucenao) for reverse image searching.

## Example service

```sh
[Unit]
Description=Beako bot container
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/docker build -t app /root/beako
ExecStart=/usr/bin/docker run --rm --network="host" --name beako app

[Install]
WantedBy=multi-user.target
```

## Series tracking and database action commands and the help command

- `/beakohelp` (sends information about the commands)
- `/add series` (has autocomplete) (adds the text channel to the list that will receive notifications, if the series is not one of the four mentioned above it will search on mangadex and add them instead)  (needs `manage_channels` permission)
- `/remove series` (remove the text channel from the list that will receive notifications, if no series argument is passed it will show the series followed on mangadex by the text channel) (needs `manage_channels` permission)
- `/manga series` (has autocomplete) (gives information about the given manga series)
- `/last series` (has autocomplete) (informs of the latest translated chapter of given series, sends a reader for MangaDex)
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

## Tag commands

- `/tag show tag` (has autocomplete) (shows the contents of the tag, sends a file if the content was added as a file)
- `/tag add tag_content tag_file` (mutually exclusive arguments, if both is passed `tag_file` will override `tab_content`) (needs `manage_guild` permission)
- `/tag remove tag` (has autocomplete) (removes the tag) (needs `manage_guild` permission)

## Util commands

- `/poll choice1 choice2 question` (creates a poll with the choices and the question, polls have a 3 minute timer before they are finished)
- `/sauce url` (search the image url you want for the source)
- `/sauce file_attachment` (search the image file you want for the source)
- `/avatar member` (shows a member's avatar or the op's if no argument is passed. may include filter buttons if the image is static)
- `/savatar member` (shows a member's avatar or the op's if no argument is passed)
- `/banner member` (shows a member's banner or the op's if no argument is passed)
- `/series` (sends a list of series available for tracking)

## osu! commands group

- `/osu profile player` (sends information about the player)
- `/osu best player` (sends player's top plays)
- `/osu recent player` (sends player's most recent plays)

## Fun commands

- `/wordle start` (start a wordle game)
- `/wordle guess` (guess a word)
- `/coin h t` (flip a coin h and t are not required)
- `/rps choice` (has choices) (play rock-paper-scissors with Betty)
- `/roll x` (rolls a random number between 1 and x(100 if no argument is passed))
- `/say message` (make the bot say something)
- `/imagesearch query` (look for an image using [the normal api](https://normal-api.tk/))

## Gif commands

- `/pout` (sends a pout gif from tenor api)
- `/pat member` (pat a member or yourself if you want)
- `/hug member` (hug a member or yourself if you so need)
- `/smug` (sends a smug gif from tenor api)

## Timer commands

- `/alarm time reason` (sets an alarm for you and pings you at that time, only works in the same day though, at least for now)
- `/remind time unit reason` (reminds the user after 'time' 'unit's (ex. 5 seconds) for 'reason' (not required), d: day(s), h: hour(s), m: minute(s), s: second(s))
- `/time timezone` (has autocomplete) (tells you the time in the timezone you want, there is a autocomplete search function for this)

## Warframe commands

- `/item order_type item_name` (has autocomplete + choices) (send info about an item as well as several orders of given type with their /w message templates)

## Tasks

- `change_avatar()` (changes avatar every 12 hours, selecting randomly from db)
- `check_chapter()` (checks the latest chapters of the followed series every minute and notifies)
- `filter_channels()` (filters out the channels that no longer exists from the db)

### TODOS

- Add more osu! functionality
- Make the results for osu! prettier, they look awful
- Add tracking for animes as well
- Steam wishlisting? idk