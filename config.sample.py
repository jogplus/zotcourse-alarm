class Config:
    # MUST be set to send notifications
    EMAIL_USERNAME = ""
    EMAIL_PASSWORD = ""

    # Opens login page in browser whenever server starts
    OPEN_WINDOW_IN_BROWSER = True
    DB_URI = "sqlite:///database.db"
    SECRET_KEY = "secret"
    PORT = 3000

    # Leave YEAR_TERM empty to automatically select current term
    YEAR_TERM = ""
    WEBSOC_BASE_URL = "https://www.reg.uci.edu/perl/WebSoc/"
    # Wait 10 - 20 seconds per request
    WAIT_TIME_LOWER = 1000
    WAIT_TIME_UPPER = 2000

    # See README for usage
    USING_NGROK = False

    # See README for usage
    USING_FIRESTORE = False
    SERVICE_ACCOUNT_FILE = ""
