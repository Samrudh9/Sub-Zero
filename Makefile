.PHONY: help install run-agent run-app run-backend run-all docker-up docker-down test lint clean

# Default target
help:
	@echo "Sub-Zero Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install all dependencies"
	@echo "  make install-agent  - Install Python agent dependencies"
	@echo "  make install-app    - Install Flutter app dependencies"
	@echo ""
	@echo "Run (Local):"
	@echo "  make run-agent      - Run the AI agent (browser test)"
	@echo "  make run-app        - Run Flutter app on Chrome"
	@echo "  make run-backend    - Run FastAPI backend server"
	@echo "  make run-temporal   - Run Temporal dev server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all services with Docker"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linters"
	@echo "  make clean          - Clean up generated files"

# ============== Setup ==============

install: install-agent install-app
	@echo "✅ All dependencies installed!"

install-agent:
	@echo "📦 Installing Python dependencies..."
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && playwright install chromium
	@echo "✅ Agent dependencies installed!"

install-app:
	@echo "📦 Installing Flutter dependencies..."
	cd mobile && flutter pub get
	@echo "✅ Flutter dependencies installed!"

# ============== Run Local ==============

run-agent:
	@echo "🤖 Starting AI Agent..."
	. venv/bin/activate && cd agent && python browser_agent.py

run-app:
	@echo "📱 Starting Flutter app on Chrome..."
	cd mobile && flutter run -d chrome

run-app-ios:
	@echo "📱 Starting Flutter app on iOS..."
	cd mobile && flutter run -d ios

run-app-android:
	@echo "📱 Starting Flutter app on Android..."
	cd mobile && flutter run -d android

run-backend:
	@echo "🖥️ Starting FastAPI backend..."
	. venv/bin/activate && cd backend && uvicorn main:app --reload --port 8000

run-temporal:
	@echo "⚙️ Starting Temporal dev server..."
	temporal server start-dev

run-worker:
	@echo "👷 Starting Temporal worker..."
	. venv/bin/activate && python -m orchestration.worker

# ============== Docker ==============

docker-up:
	@echo "🐳 Starting all services with Docker..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   - Backend API: http://localhost:8000"
	@echo "   - Temporal UI: http://localhost:8233"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build --no-cache

# ============== Development ==============

test:
	@echo "🧪 Running tests..."
	. venv/bin/activate && pytest -v

test-agent:
	. venv/bin/activate && pytest agent/ -v

test-backend:
	. venv/bin/activate && pytest backend/ -v

lint:
	@echo "🔍 Running linters..."
	. venv/bin/activate && ruff check .
	. venv/bin/activate && black --check .

format:
	@echo "✨ Formatting code..."
	. venv/bin/activate && black .
	. venv/bin/activate && ruff check --fix .

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .ruff_cache 2>/dev/null || true
	@echo "✅ Cleaned!"

# ============== Quick Start ==============

quickstart: install
	@echo ""
	@echo "🥶 Sub-Zero is ready!"
	@echo ""
	@echo "Quick start options:"
	@echo "  1. Run 'make run-app' to start the mobile app"
	@echo "  2. Run 'make docker-up' to start all backend services"
	@echo "  3. Run 'make run-agent' to test the AI agent"
	@echo ""
	@echo "Don't forget to set your ANTHROPIC_API_KEY in .env!"
