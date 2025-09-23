# Hackathon Evaluator Service

A Flask-based central evaluator service for hackathon competitions. This service sends test data to participants, evaluates their submissions, maintains a leaderboard, and provides a web interface for real-time results.

🌐 **Live Service**: https://hackathon-evaluator.onrender.com

## 🚀 Features

- **Test Data Distribution**: Generates and serves deterministic test data to participants
- **Automated Evaluation**: Evaluates submissions based on configurable criteria (accuracy, performance, completeness)
- **Live Leaderboard**: Real-time leaderboard with web interface and auto-refresh
- **REST API**: Complete API for participant interactions with proper validation
- **Configuration System**: YAML-based configuration management
- **Deployment Ready**: Ready for Render deployment with health checks

## 📁 Project Structure

```
hackathon_evaluator/
├── app.py                        # Main Flask application
├── leaderboard_manager.py        # Leaderboard management
├── evaluator.py                  # Evaluation engine
├── test_data_provider.py         # Test data generation
├── config_manager.py             # Configuration management
├── templates/                    # HTML templates
│   ├── leaderboard.html          # Leaderboard frontend
│   └── error.html                # Error page
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
Get test data for processing. Returns deterministic test cases based on participant name.

**Parameters:**
- `participant_name` (required): Name of the participant/team  
- `submission_tag` (optional): Submission version tag (defaults to "default")

**Example Request:**
```bash
curl "https://hackathon-evaluator.onrender.com/api/test-data?participant_name=TeamAlpha&submission_tag=v1.0"
```

**Response:**
```json
{
  "status": "success",
  "test_data": {
    "test_data_id": "unique_16_char_id",
    "participant_name": "TeamAlpha",
    "submission_tag": "v1.0",
    "timestamp": "2024-01-01T12:00:00.000000",
    "test_cases": [
      {
        "test_id": "simple_math_1",
        "type": "simple_math",
        "description": "Basic mathematical operations",
        "input_data": {
          "operation": "add",
          "numbers": [5, 3]
        },
        "expected_output_format": {
          "result": "Numeric result of the operation",
          "operation_performed": "Description of operation"
        }
      }
    ],
    "instructions": {
      "description": "Process the provided test cases and return results",
      "expected_format": {...},
      "submission_endpoint": "/api/submit-results"
    },
    "evaluation_criteria": {
      "accuracy": "Correctness of results (40%)",
      "performance": "Processing efficiency (30%)",
      "completeness": "Coverage and metadata (30%)"
    }
  }
}
```

### POST `/api/submit-results`
Submit processed results for evaluation. **Critical**: Both `processed_data` and `metadata` fields are required.

**Required Fields:**
- `participant_name` (string): Name of the participant/team
- `submission_tag` (string): Submission version tag
- `test_data_id` (string): ID from the test data request
- `results` (object): Must contain both `processed_data` and `metadata`

**Example Request:**
```bash
curl -X POST https://hackathon-evaluator.onrender.com/api/submit-results \
-H "Content-Type: application/json" \
-d '{
  "participant_name": "TeamAlpha",
  "submission_tag": "v1.0",
  "test_data_id": "abc123def456",
  "results": {
    "processed_data": {
      "simple_math_1": {
        "result": 8,
        "operation_performed": "add on [5, 3]"
      },
      "text_processing_1": {
        "result": "HELLO WORLD",
        "original_text": "Hello World",
        "task_completed": true
      }
    },
    "metadata": {
      "processing_time_seconds": 1.5,
      "memory_usage_mb": 85,
      "quality_checks_passed": true,
      "validation_status": "passed"
    }
  }
}'
```

**Response:**
```json
{
  "status": "success",
  "score": 0.856,
  "rank": 3,
  "evaluation_details": {
    "accuracy_score": 0.825,
    "performance_score": 0.910,
    "completeness_score": 1.0,
    "weighted_scores": {
      "accuracy": 0.330,
      "performance": 0.273,
      "completeness": 0.300
    },
    "criteria_weights": {
      "accuracy": 0.4,
      "performance": 0.3,
      "completeness": 0.3
    }
  },
  "message": "Submission successful! Score: 0.856"
}
```

### GET `/api/leaderboard`
Get current leaderboard data with all participants and scores.

**Example Request:**
```bash
curl https://hackathon-evaluator.onrender.com/api/leaderboard
```

**Response:**
```json
{
  "status": "success",
  "leaderboard": [
    {
      "participant_name": "TeamAlpha",
      "submission_tag": "v1.0",
      "score": 0.93,
      "formatted_score": "0.930",
      "rank": 1,
      "timestamp": "2024-01-01T12:00:00.000000"
    }
  ],
  "total_participants": 5
}
```

### GET `/api/health`
Health check endpoint for monitoring service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "service": "hackathon-evaluator"
}
```

### GET `/`
Web interface showing the leaderboard with auto-refresh every 30 seconds.

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

### Automated Test Workflow
Run the complete test workflow to simulate multiple participants:

```bash
python test_workflow.py
```

**What it does:**
1. **Requests test data** for 3 teams: TeamAlpha, TeamBeta, TeamGamma
2. **Processes test cases** with mock algorithms:
   - Simple math: addition, multiplication, subtraction
   - Text processing: word count, reverse, uppercase
   - Data analysis: mean, max, sum calculations
3. **Submits results** with realistic metadata (processing time, memory usage)
4. **Displays rankings** and leaderboard updates

### Manual Testing Examples

**Test data request:**
```bash
curl "https://hackathon-evaluator.onrender.com/api/test-data?participant_name=TestTeam&submission_tag=v1.0"
```

**Submit a high-scoring result:**
```bash
curl -X POST https://hackathon-evaluator.onrender.com/api/submit-results \
-H "Content-Type: application/json" \
-d '{
  "participant_name": "TestTeam",
  "submission_tag": "v1.0",
  "test_data_id": "your_test_data_id",
  "results": {
    "processed_data": {
      "simple_math_1": {"result": 42, "operation_performed": "add on [20, 22]"},
      "text_processing_1": {"result": "HELLO WORLD", "original_text": "Hello World", "task_completed": true}
    },
    "metadata": {
      "processing_time_seconds": 0.5,
      "memory_usage_mb": 45,
      "quality_checks_passed": true,
      "validation_status": "passed"
    }
  }
}'
```

**Check results:**
- Leaderboard: https://hackathon-evaluator.onrender.com
- API: `curl https://hackathon-evaluator.onrender.com/api/leaderboard`

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

### Current Live Deployment
- **Service URL**: https://hackathon-evaluator.onrender.com
- **Platform**: Render.com
- **Status**: Active and ready for submissions

### Render Deployment

1. **Connect Repository**: Link your GitHub repo to Render
2. **Configure Service**:
   - **Build Command**: `pip install -r requirements.txt`  
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Root Directory**: Leave empty (files are in project root)
3. **Environment Variables**:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your_secret_key
   PORT=10000
   LEADERBOARD_CSV_PATH=data/leaderboard.csv
   ```
4. **Deploy**: Render automatically deploys on git push

### Manual Deployment

For other platforms, use the Flask app directly:

```bash
# Production with Gunicorn
gunicorn --bind 0.0.0.0:$PORT app:app

# Development
python run_local.py
```

### Health Check
Monitor deployment status:
```bash
curl https://hackathon-evaluator.onrender.com/api/health
```

## 🏆 Evaluation System

The evaluation engine scores submissions based on three weighted criteria:

### Scoring Breakdown
1. **Accuracy (40% weight)**: Correctness of results against expected outcomes
   - Based on processed_data quality and completeness
   - Mock scoring uses deterministic randomization for demonstration
   - Range: 0.6 to 0.95 base score + completeness bonus

2. **Performance (30% weight)**: Processing efficiency metrics
   - **Time Performance**: Scored against 10.0 second threshold
   - **Memory Performance**: Scored against 1000MB threshold  
   - Better performance = higher score
   - Missing metrics default to 0.5 score

3. **Completeness (30% weight)**: Coverage and metadata quality
   - **Data Processing** (0.5 points): Results provided in processed_data
   - **Metadata Provided** (0.2 points): Metadata object included
   - **Quality Checks** (0.2 points): quality_checks_passed = true
   - **Validation Status** (0.1 points): validation_status = "passed"

### Score Calculation
```
final_score = (accuracy × 0.4) + (performance × 0.3) + (completeness × 0.3)
```

### Validation Requirements
**Critical**: Submissions must include both fields in the `results` object:
- `processed_data`: Dictionary with test case results (test_id → result object)
- `metadata`: Dictionary with performance and quality metrics

Missing either field will result in validation error and 0.0 score.

## 🔄 Participant Workflow

### Step-by-Step Process

1. **Request Test Data**
   ```bash
   curl "https://hackathon-evaluator.onrender.com/api/test-data?participant_name=YourTeamName&submission_tag=v1.0"
   ```
   - Save the `test_data_id` from the response
   - Review the test cases and expected output formats

2. **Process the Test Cases**
   - Implement your algorithm to solve each test case
   - Current test types: `simple_math`, `text_processing`, `data_analysis`
   - Ensure you handle all test cases in the provided data

3. **Format Your Results**
   ```json
   {
     "processed_data": {
       "test_id_1": {"result": "your_result", "additional_fields": "..."},
       "test_id_2": {"result": "your_result", "additional_fields": "..."}
     },
     "metadata": {
       "processing_time_seconds": 1.5,
       "memory_usage_mb": 85,
       "quality_checks_passed": true,
       "validation_status": "passed"
     }
   }
   ```

4. **Submit Results**
   ```bash
   curl -X POST https://hackathon-evaluator.onrender.com/api/submit-results \
   -H "Content-Type: application/json" \
   -d '{"participant_name":"YourTeamName","submission_tag":"v1.0","test_data_id":"saved_id","results":{...}}'
   ```

5. **Check Your Ranking**
   - Visit: https://hackathon-evaluator.onrender.com
   - Or API: `GET /api/leaderboard`

## 📊 Leaderboard Features

- Real-time updates after each submission
- Automatic ranking by score (descending)
- Keeps best score per participant
- Auto-refresh every 30 seconds
- Mobile-friendly interface
- Shows participant name, submission tag, score, and timestamp

## 🛠️ Customization

### Adapting for Your Hackathon

1. **Test Data Generation** (`test_data_provider.py`):
   ```python
   # Add new test types to _initialize_data_templates()
   "your_test_type": {
       "description": "Your test description",
       "sample_data": [{"input": "sample", "task": "process"}]
   }
   ```

2. **Evaluation Logic** (`evaluator.py`):
   - Modify `_calculate_accuracy_score()` for your scoring algorithm
   - Update `_validate_submission_format()` for custom validation rules
   - Adjust performance thresholds in the constructor

3. **Scoring Configuration** (`config/config.yaml`):
   ```yaml
   evaluation:
     criteria_weights:
       accuracy: 0.4    # Adjust weight distribution
       performance: 0.3
       completeness: 0.3
     scoring:
       base_score_range: {min: 0.6, max: 0.95}
       performance_time_threshold: 10.0  # seconds
       performance_memory_threshold: 1000.0  # MB
   ```

4. **Frontend Customization** (`templates/leaderboard.html`):
   - Update styling, branding, and display format
   - Modify auto-refresh interval (currently 30 seconds)
   - Add custom participant information fields

### Common Modifications
- **Change test case types**: Edit the templates in `TestDataProvider._initialize_data_templates()`
- **Adjust scoring weights**: Modify `criteria_weights` in config
- **Add performance metrics**: Extend the metadata validation and scoring
- **Custom leaderboard fields**: Update CSV headers and frontend display

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## 🚨 Common Issues & Solutions

### Submission Validation Errors
- **"Missing required field: processed_data"**: Ensure your `results` object contains both `processed_data` and `metadata` fields
- **"processed_data must be a dictionary"**: Format as `{"test_id": {"result": "value"}}`
- **Low accuracy scores**: Check that your results match expected test case formats

### Performance Optimization
- Keep `processing_time_seconds` under 10.0 for best performance score
- Memory usage under 1000MB is optimal
- Set `quality_checks_passed: true` and `validation_status: "passed"` in metadata

### Deployment Issues
- **Import errors**: Ensure all Python files are in the repository root (not in `src/` subdirectory)
- **Module not found**: Check that files aren't excluded by `.gitignore` patterns
- **Health check fails**: Verify the service is running on the correct port with proper environment variables

---

**Ready to compete? Visit https://hackathon-evaluator.onrender.com and start your submission! 🎉**
