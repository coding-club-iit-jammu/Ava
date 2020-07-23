# Ava
The discord bot for our Coding Club IIT Jammu discord(development server) written in Python

[![Build status](https://vsrm.dev.azure.com/abhishek0220/_apis/public/Release/badge/7a8e80e6-4b2a-4e0d-b9bc-7cc323c6c403/1/1)](https://dev.azure.com/abhishek0220/BOT_Ava/_release?definitionId=0)
# Instructions to Run locally and contribute
1. Install [Python](https://www.python.org/downloads/).
2. Clone this repository and open terminal, change directory to the repo.
3. Run `python -m venv ./venv` to create virtual environment.
4. Run `venv\Scripts\activate` command to activate virtual environment.
5. Run `pip install -r reqirements.txt` command to install dependencies.
6. Create a **.env** file in the folder, containing

```
DISCORD_TOKEN = <token>
SERVER = <server_id>
```
You can create a demo server and a bot application for testing purpose. Details [here](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot).

7. Push the changes in a separate branch and create a pull request. After the PR is merged, it will be automatically deployed to Azure VM via Azure Pipelines.
