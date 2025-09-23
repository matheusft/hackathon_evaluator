# Hackathon Evaluator Service

A Flask-based central evaluator service for hackathon competitions. This service sends test data to participants, evaluates their submissions, maintains a leaderboard, and provides a web interface for real-time results.

## 🚀 Features

- **Test Data Distribution**: Generates and serves test data to participants
- **Automated Evaluation**: Evaluates submissions based on configurable criteria
- **Live Leaderboard**: Real-time leaderboard with web interface
- **REST API**: Complete API for participant interactions
- **Configuration System**: YAML-based configuration management
- **Deployment Ready**: Ready for Render deployment

## 📁 Project Structure

```
hackathon_evaluator/
├── src/                           # Source code
│   ├── app.py                    # Main Flask application
│   ├── leaderboard_manager.py    # Leaderboard management
│   ├── evaluator.py              # Evaluation engine
│   ├── test_data_provider.py     # Test data generation
│   ├── config_manager.py         # Configuration management
│   └── templates/                # HTML templates
│       ├── leaderboard.html      # Leaderboard frontend
│       └── error.html            # Error page
├── config/
│   └── config.yaml               # Configuration file
├── data/
│   └── leaderboard.csv           # Leaderboard data storage
├── run_local.py                  # Local development runner
├── wsgi.py                       # Production WSGI entry point
├── render.yaml                   # Render deployment config
├── requirements.txt              # Python dependencies
└── test_workflow.py              # Testing script
```

## 🔧 API Endpoints

### GET `/api/test-data`
Get test data for processing.

**Parameters:**
- `participant_name` (required): Name of the participant/team
- `submission_tag` (optional): Submission version tag

**Response:**
```json
{
  "status": "success",
  "test_data": {
    "test_data_id": "unique_id",
    "test_cases": [...],
    "instructions": {...}
  }
}
```

### POST `/api/submit-results`
Submit processed results for evaluation.

**Payload:**
```json
{
  "participant_name": "TeamName",
  "submission_tag": "v1.0",
  "test_data_id": "unique_id",
  "results": {
    "processed_data": {...},
    "metadata": {
      "processing_time_seconds": 2.5,
      "memory_usage_mb": 100,
      "quality_checks_passed": true,
      "validation_status": "passed"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "score": 0.856,
  "rank": 3,
  "evaluation_details": {...}
}
```

### GET `/api/leaderboard`
Get current leaderboard data.

### GET `/api/health`
Health check endpoint.

### GET `/`
Web interface showing the leaderboard.

## 🏃‍♂️ Running Locally

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the development server:**
```bash
python run_local.py
```

3. **Access the service:**
- Leaderboard: http://localhost:5001
- API: http://localhost:5001/api/

## 🧪 Testing

Run the test workflow to simulate participant interactions:

```bash
python test_workflow.py
```

This will:
1. Request test data for multiple participants
2. Process the data (mock processing)
3. Submit results
4. Display leaderboard rankings

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- **Evaluation criteria weights** (accuracy, performance, completeness)
- **Scoring parameters** (thresholds, bonuses)
- **Server settings** (host, port, debug)
- **Test data templates**

### Environment Variables

For production deployment, set these environment variables:
- `SECRET_KEY`: Flask secret key
- `PORT`: Server port (defaults to 5001)
- `LEADERBOARD_CSV_PATH`: Path to leaderboard CSV file
- `ENVIRONMENT`: Set to "production" for production settings

## 🚀 Deployment

### Render Deployment

1. Connect your repository to Render
2. The `render.yaml` file configures automatic deployment
3. Set environment variables in Render dashboard
4. Deploy!

### Manual Deployment

For other platforms, use the WSGI entry point:

```bash
gunicorn --bind 0.0.0.0:$PORT src.app:app
```

## 🏆 Evaluation System

The evaluation engine scores submissions based on three criteria:

1. **Accuracy (40%)**: Correctness of results
2. **Performance (30%)**: Processing efficiency (time/memory)
3. **Completeness (30%)**: Coverage and metadata quality

Scores are calculated using configurable thresholds and combined into a final weighted score.

## 🔄 Participant Workflow

1. **Request test data:** `GET /api/test-data?participant_name=TeamName`
2. **Process the data:** Apply your algorithm to the test cases
3. **Submit results:** `POST /api/submit-results` with processed data
4. **Check leaderboard:** View rankings at the web interface

## 📊 Leaderboard Features

- Real-time updates after each submission
- Automatic ranking by score (descending)
- Keeps best score per participant
- Auto-refresh every 30 seconds
- Mobile-friendly interface
- Shows participant name, submission tag, score, and timestamp

## 🛠️ Customization

To adapt for your specific hackathon:

1. **Modify test data generation** in `src/test_data_provider.py`
2. **Update evaluation logic** in `src/evaluator.py`
3. **Adjust scoring criteria** in `config/config.yaml`
4. **Customize frontend** in `src/templates/leaderboard.html`

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

---

**Happy Hacking! 🎉**# Trigger deployment after fixing Root Directory
# Force deployment refresh
