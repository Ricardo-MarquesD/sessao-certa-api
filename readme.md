Para executar o projeto:
poetry run python -m uvicorn main:app --reload --port 8000 --app-dir src

ngrok:
ngrok http 8000