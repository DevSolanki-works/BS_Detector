FROM python:3.12-slim

WORKDIR /app

# Step 1: Upgrade pip to handle modern wheels better
RUN pip install --upgrade pip

# Step 2: Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]