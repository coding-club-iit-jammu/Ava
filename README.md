# Ava
The discord bot for our Coding Club IIT Jammu discord(development server) written in Python

[![Build status](https://vsrm.dev.azure.com/abhishek0220/_apis/public/Release/badge/7a8e80e6-4b2a-4e0d-b9bc-7cc323c6c403/1/1)](https://dev.azure.com/abhishek0220/BOT_Ava/_release?definitionId=0)
[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Technology stack

- Python 3.7
- Database : Azure Cosmos DB
- Database API - MongoDB API
- Deploy: Azure Pipelines
- Server: Azure Virtual Machine

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
MONGODB = <mongodb_uri>
DEBUG = "True"
DEPARTMENT_CHANNEL = <department_selection_channel_id>
LOG_CHANNEL = <log_channel_id>
DEPARTMENT_MESSAGE = <department_selection_message>
SENDGRID_API_KEY = <sendgrid_key_optional_with_DEBUG>
```

7. For using Google OAuth 2.0 for verifying users.
   - Register a project on Google Cloud Platform
   - Goto API & Services dashboard.
   - Consider Constent Screen. `userinfo.email` scope is required to run this application.
   - Create a new Credential (Oauth Client ID). Select application type `Desktop app`.
   - Download `client_secret.json` file and place it at the project root.
   - Enjoy!

You can create a demo server and a bot application for testing purpose. Details [here](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot).

8. Push the changes in a separate branch and create a pull request. After the PR is merged, it will be automatically deployed to Azure VM via Azure Pipelines.
