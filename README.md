**v. 0.0.1**

**This bot is designed to transfer information from Steam to the Telegramm group.
The bot does two things:**
1. It displays the status of players in a static message in the group, updating every 10 minutes.

2. If the message cannot be edited (Telegram's 48-hour limit), the bot deletes the old message and sends a new one.

3. Each time a player from players.json enters a game, the bot notifies this with a separate message.

4. When the game is closed, the bot also notifies this.

5. The bot is a simple information service that has proven useful for us and our friends to track each other's activity.

6. In the future, the “Game Scoreboard” will be expanded to display detailed current sessions for Dota2 and CS2 games in the following format:<br/>
🎮 Player1<br/>
└─ 🧙♂️ Windranger (Lvl 18<br/>
   ├─ K/D/A: 8/2/14<br/>
   ├─ 🧪 Items: MKB, Maelstrom, BKB... <br/> 
   └─ ⏱ 32:15<br/>  

🎮 Player2  
└─ 🔫 CS2 | Competitive  
   ├─ 🗺 Map: de_mirage  
   ├─ K/D: 12/8 | 💣 3 plants  
   └─ ⏱ Score: 10-7 (CT)  

7. Currently using SQLite, with plans to transition to a cloud database in the future

8. Currently, the bot is being developed locally for a specific list of players. In the future, the following will be developed:
- There will be a single, shared bot for each group (no need to run a separate bot for each company)
- The bot will work with a regular SQL service, which will not fill in a specific list of players, but will add it /add SteamID64 to a specific group (chat/channel)
- Use of webhooks for instant updates
- A separate module for each game (CS2/Dota2/Pubg, etc.)
- Data updates every 2-3 minutes (the game scoreboard will become more relevant)


      




Before launching it you need to:
1. Install dependencies

`pip install python-telegram-bot requests python-dotenv`

2. Get Steam API Key

`https://steamcommunity.com/dev/apikey`

3. Fill players.json with SteamID64 players

`https://steamid.io/lookup/`

4. initialize the database:

`python -c “from database import init_db; init_db()”`

5. Fill in .env 

>TELEGRAM_BOT_TOKEN from @BotFather

>STEAM_API_KEY from https://steamcommunity.com/dev/apikey

6. Launch the bot (VS Code was used)

`python bot.py`

7. Add the bot to the group 

Send command:

`/start@your_bot_name`
>For example: /start@MySteamTrackerBot

The bot will respond with a confirmation and save the chat_id. After that it will start working automatically!

8. Player status updates will start
