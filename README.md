# Zotcourse Alarm

Get an email and text message notification when a course opens up!

Login Page            |  Home Page
:-------------------------:|:-------------------------:
![Login Screenshot](https://imgur.com/ILFXNEy.png) |  ![Home Screenshot](https://i.imgur.com/zQkxKan.png)

## Setup

1. Create and activate your python virtual env:
    ```
    $ python3 -m venv env
    $ source env/bin/activate
    ```
2. Navigate to the root of the zotcourse-alarm folder, and run the following:
    ```
    $ cd zotcourse-alarm
    $ pip3 install -r requirements.txt
    ```
3. Create a duplicate of the sample config and database using:
    ```
    $ cp config.sample.py config.py
    $ cp database.sample.db database.db
    ```
4. Fill in your email's username and password in `config.py`. This will be the account that sends the notification when a course opens up. If you use a Google account, you will need to go to https://myaccount.google.com/u/0/lesssecureapps and enable "Less secure app access" so that it can send the notifications. This setting automatically turns off after a couple of weeks so you will have to re-enable it if sending notifications fail.
5. Run the project using:
    ```
    $ python3 app.py
    ```

## (Optional) Ngrok Setup
This allows you to use the Ngrok service so that your instance of Zotcourse Alarm can be accessible from anyone who has the link.
1. Place your downloaded `ngrok` executable from https://ngrok.com/ in the root directory of the project.
2. In `config.py` set `USING_NGROK = True`

## (Optional) Google Firestore/App Engine Setup
This is a workaround to the Ngrok limitiation where each time Ngrok is run, a new random link is generated. Everytime Zotcourse Alarm starts up, it saves the generated Ngrok URL in Firestore. Using an App Engine instance as a simple redirect server, we redirect the user to the saved Ngrok URL. As a result, we can use the static URL from an App Engine instance to redirect to the dyanamic URL of Nrgok instance.
1. Follow [this tutorial on setting up](https://cloud.google.com/appengine/docs/standard/python3/quickstart) Google Cloud Platform (GCP).
2. Follow [this tutorial in order to deploy](https://cloud.google.com/appengine/docs/standard/python3/quickstart) the redirect server in `/redirect_server`
3. Go to your GCP Console and create a Firestore instance and App Engine instance. Then go to the "API's & Services / Credentials" section. Under "Service Accounts" click on the service account and create a key. Place the downloaded json file in the root directory of the project and set the file name for `SERVICE_ACCOUNT_FILE` in `config.py`.
4. In `config.py` set `USING_FIRESTORE = True`
