# Hackathon Evaluator Service

A Flask-based evaluator service for hackathon competitions with test data distribution, automated evaluation, and live leaderboard.

🌐 **Live Service**: https://hackathon-evaluator.onrender.com

## Features

- **Test Data Distribution**: Generates deterministic test data from JLR vehicle configurations
- **Automated Evaluation**: Scores submissions using 10 specialized embedding quality tests
- **Live Leaderboard**: Real-time PostgreSQL-based leaderboard with web interface
- **REST API**: Complete API for participant interactions and submission evaluation

## Project Structure

```
hackathon_evaluator/
├── app.py                     # Main Flask application
├── wsgi.py                    # WSGI entry point for production
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment configuration
├── src/
│   ├── core/
│   │   ├── evaluator.py       # Evaluation engine
│   │   ├── leaderboard_manager.py # Leaderboard management
│   │   └── test_data_provider.py # Test data generation
│   └── utils/
│       └── run_local.py       # Local development server
├── scripts/
│   └── test_workflow.py       # Testing and demo script
├── config/
│   ├── config_manager.py      # Configuration loader
│   └── config.yaml            # YAML configuration
├── data/
│   └── jlr_vehicle_configurations.csv # Vehicle data
└── templates/                 # HTML frontend templates
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   python src/utils/run_local.py
   ```

3. **Access service:**
   - Leaderboard: http://localhost:5001
   - API: http://localhost:5001/api/

## API Endpoints

### GET `/api/test-data`
Get test data for processing.
- **Parameters**: `participant_name` (required), `submission_tag` (optional)

### POST `/api/submit-results`
Submit processed results for evaluation.
- **Required**: `participant_name`, `submission_tag`, `test_data_id`, `results`
- **Results format**: Must include both `processed_data` and `metadata` objects

### GET `/api/leaderboard`
Get current leaderboard data.

### GET `/api/health`
Health check endpoint.

## Testing

Run the automated test workflow:
```bash
python scripts/test_workflow.py
```

This simulates multiple participants and displays leaderboard updates.

## Deployment

**Current deployment**: Render.com with automatic deploys on git push.

**Environment variables**:
- `ENVIRONMENT=production`
- `SECRET_KEY=auto-generated`
- `DATABASE_URL=auto-configured-from-postgresql-database`

## Evaluation System

Submissions are scored using **10 specialized embedding quality tests** with the following weights:

- **Price Extremes (15%)**: Most/least expensive vehicles should be dissimilar
- **Single Option Difference (15%)**: Configs differing by 1 option should be highly similar
- **Model Year Sensitivity (10%)**: Year differences should have moderate impact
- **Color Sensitivity (10%)**: Color-only differences should have minimal impact
- **Trim Level Similarity (10%)**: Same vehicle/year, different trims should cluster
- **Vehicle Line Separation (10%)**: Different vehicle lines should be clearly separated
- **Derivative Clustering (10%)**: Same derivatives should cluster together
- **Feature Count Correlation (10%)**: Feature count should correlate with similarity
- **Transitivity (5%)**: If A~B and B~C, then A should be similar to C
- **Cross-Year Comparison (5%)**: Same configs across years should be moderately similar

Each test uses cosine similarity with configurable thresholds. The final score is the weighted sum of all test scores.