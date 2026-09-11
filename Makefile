setup:
	pip install -r requirements.txt

pipeline:
	python run_pipeline.py

test:
	pytest -q

dashboard:
	streamlit run app.py

api:
	uvicorn api:app --reload
