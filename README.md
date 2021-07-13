# expensify_bot

A personal telegram bot for creating expensify report diretly from an expense PDF.

## Why not Slack bot?

There are company restrictions on Slack bot, hence Telegram bot.

## Why private bot?

Intended to be used as a private assistant + due to sensitive information involved in automating this, opting for a safe & secure option.
Considering the confidential nature of the data invovled in the automation, opt for appropriate [hosting options](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots).

Recommended Hosting Option: devVM/UBVM

## How to set it up?

1. Create a telegram bot by following this [documentation](https://core.telegram.org/bots/#3-how-do-i-create-a-bot) that will provide you an API KEY

2. Though this bot can be searched publicly, we will make this bot a personal/private assistant by following the steps below.

    a. Open this URL, replace <XXX: YYYYY> with your bot API Key
    https://api.telegram.org/bot<XXX:YYYYY>/getUpdates
    b. Send a /start command or 'Hi' message to your bot.
    c. After b), refresh the URL, the web page should show a JSON, from which you can grab the 'chat.id' (It's an integer)

3. Generate Expensify UserID and Secret by following this [documentation](https://integrations.expensify.com/Integration-Server/doc/#authentication)

4. git clone https://github.com/premkarat/expensify_bot.git

5. cd expensify_bot; pip install -r requirements.txt (Optionally create a virtual environment)

6. Edit config.py and provide following configuration

    a. Config.TELEGRAM.API_KEY
    b. Config.TELEGRAM.CHAT_ID

    c. Config.EXPENSIFY.USERID
    d. Config.EXPENSIFY.SECRET

    e. Config.EXPENSIFY.EMP_MAILID
    f. Config.OKTA.USERNAME
    g. Config.OKAT.PASSWORD

7. Start the bot, using the following command
    python bot.py &
