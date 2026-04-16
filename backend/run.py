import os
from dotenv import load_dotenv

# Load .env from the project root (one level above /backend)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2222)
