# Mallya
A simple ChatBot to attend to freshers' queries and your general bakar too.

# Setup for Development
* Clone the project : `git clone https://github.com/manavmehta/mallya.git`
* Now run the following commands
```python
pip3 install -r requirements.txt
```
* Copy/Move service_account.json to the following path.
(Linux/Mac: "~/.config/gspread/service_account.json")
(Windows: "%APPDATA%\gspread\service_account.json")
* Make sure that mongodb server is up and running on your test machine by using `mongo` command on your terminal.
```mongod --port 27017 --dbpath ~/mongodb/```
* Now run the following commands:
```python
python3 initdb.py
python3 app.py
```

# Instructions to add Mallya to your Telegram
* Add Mallya to your Telegram by clicking [this link](https://t.me/MallyaBot)
* Chat with the King of good times
