# Sync Google Tasks & Microsoft To Do
This project allows to sync tasks between Google Task and Microsoft To Do

## Actual limitations
- Only sync the default task list
- Do not delete task automatically
- Only sync title, description, status and due date. Other properties like files and reminder are not synced.
- Each time the app is started, a new authentification must be done with Microsoft

# Installation
## The application
- You must have `Python 3`, it is prefered to have at least `Python 3.11` as it has been developped for this version of Python
- Clone the github project
- Run this command at the root of the project to install the packages `pip install -r requirements.txt `
## Access to Google API
- Follow the guide in `Set up your environment` from [developers.google.com/tasks/quickstart/python](https://developers.google.com/tasks/quickstart/python?hl=en)
- Once you have the file `credentials.json` put all its content in the file `config/config.cfg` in `[google-api] credentials`. The json must be on one line.
## Access to Micorosft Azure API
- Follow the guide in `Register the app in the portal` from [learn.microsoft.com/en-us/graph/tutorials/python?tabs=aad&tutorial-step=1](https://learn.microsoft.com/en-us/graph/tutorials/python?tabs=aad&tutorial-step=1)
- In the azure app permissions, you must allow to following permissions `User.Read Tasks.Read Tasks.Read.Shared Tasks.ReadWrite Tasks.ReadWrite.Shared`
- In the file `config/config.cfg` add in `[azure] clientId`, the client id of your azure application
## Configure the application
- You can choose the sync interval in `config/config.cfg`

# Run
- To run the app, you only have to run the `main.py` file with python
- At the start a message like this will appear in the console : 
```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code XXXXXX to authenticate.

```
You will have to follow the link, enter the code, log to your microsoft account and accept the permissions. Unfortunately, at the current state of the project, this step will have to be redone at each start of the app. 
- All the logs will be displayed in the console and also in files in the directory `logs`