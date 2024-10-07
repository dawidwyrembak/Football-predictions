# Football-predictions

This is a simple Python 3.8 web application developed for an engineering thesis (2021). It predicts football match results as a bookmaker odds using data scrapped from the web.

## Requirements

- Python 3.8
- Google Chrome
- Dependencies from `requirements.txt`
- The app requires updating for the current seasons. All data was created before 2021-06.

## Installation

1. Clone this repository.

2. Install required Python libraries in your venv:
    ```bash
    pip install -r requirements.txt
    ```

4. Make sure you have all needed data (`preprocess_table.py`).

## Running the App

1. Run the server:
    ```bash
    python manage.py runserver
    ```

2. Open **Google Chrome** and go to:
    ```
    http://127.0.0.1:8000
    ```

## License

This project was created for an engineering thesis.
