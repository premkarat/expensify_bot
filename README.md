# expensify_bot

A personal telegram bot for creating expensify report diretly from an expense PDF.

## Why not Slack bot?

There are company restrictions on Slack bot, hence Telegram bot.

## Why private bot?

Intended to be used as a private assistant + due to sensitive information involved in automating this, opting for a safe & secure option.
Considering the confidential nature of the data invovled in the automation, opt for appropriate [hosting options](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots).

Recommended Hosting Option: devVM/UBVM

## How to setup UBVM?

1. Install GNOME desktop for selenium
sudo yum groups install "GNOME Desktop"

 If error, [RHEL 7 / Cent OS 7 – “fwupdate-efi” conflicts with “grub2-common”] is shown while executing 1), then run the following

sudo yum upgrade grub2 firewalld
sudo yum update --security

2. Enable graphical target
sudo systemctl enable graphical.target --force
sudo rm '/etc/systemd/system/default.target'
sudo ln -s '/usr/lib/systemd/system/graphical.target' '/etc/systemd/system/default.target'

3. Install chrome browser
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum localinstall google-chrome-stable_current_x86_64.rpm

4. Reboot the system for GUI to kick in
sudo reboot


## How to setup expensify personal bot?

**Python Version: 3.65 or above**

1. Create a telegram bot by following this [documentation](https://core.telegram.org/bots/#3-how-do-i-create-a-bot) that will provide you an API KEY

2. Though this bot can be searched publicly, we will make this bot a personal/private assistant by following the steps below.

    a. Open this URL, replace <XXX: YYYYY> with your bot API Key
    https://api.telegram.org/bot<XXX:YYYYY>/getUpdates
    b. Send a /start command or 'Hi' message to your bot.
    c. After b), refresh the URL, the web page should show a JSON, from which you can grab the 'chat.id' (It's an integer)

3. Generate Expensify UserID and Secret by following this [documentation](https://integrations.expensify.com/Integration-Server/doc/#authentication)

4. git clone https://github.com/premkarat/expensify_bot.git

5. cd expensify_bot; pip install -r requirements.txt (Optionally create a virtual environment)

6. cp config.py.example to config.py and edit following configuration

    a. Config.TELEGRAM.API_KEY
    b. Config.TELEGRAM.CHAT_ID

    c. Config.EXPENSIFY.USERID
    d. Config.EXPENSIFY.SECRET

    e. Config.EXPENSIFY.EMP_MAILID
    f. Config.OKTA.USERNAME
    g. Config.OKAT.PASSWORD

7. Start the bot, using the following command
    python3 bot.py &
