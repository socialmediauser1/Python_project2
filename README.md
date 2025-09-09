1. Create virtual environment:
   python -m venv venv
   venv\Scripts\activate
2. Install dependencies:
   pip install -r requirements.txt
3. Run the application:
   waitress-serve --host=127.0.0.1 --port=8000 main:app