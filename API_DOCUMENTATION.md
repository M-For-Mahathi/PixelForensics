# PixelForensics API Documentation

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Health Check
**GET** `/status`

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-10-22T22:30:00"
}
```

### 2. Detect Deepfake (MAIN ENDPOINT)
**POST** `/detect-deepfake`

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image or video)

**Supported formats:**
- Images: .jpg, .jpeg, .png, .gif, .bmp
- Videos: .mp4, .avi, .mov, .mkv

**Response (Image):**
```json
{
  "success": true,
  "file_type": "image",
  "prediction": "FAKE",
  "confidence": 89.45,
  "raw_score": 0.8945,
  "filename": "20241022_123456_test.jpg",
  "timestamp": "2024-10-22T12:34:56"
}
```

**Response (Video):**
```json
{
  "success": true,
  "file_type": "video",
  "prediction": "REAL",
  "confidence": 72.30,
  "raw_score": 0.2770,
  "frames_analyzed": 15,
  "consistency": 85.5,
  "filename": "20241022_123456_test.mp4",
  "timestamp": "2024-10-22T12:34:56"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

### 3. Get Statistics
**GET** `/api/stats`

Response:
```json
{
  "success": true,
  "stats": {
    "total_predictions": 150,
    "fake_detected": 65,
    "real_detected": 85,
    "images_processed": 120,
    "videos_processed": 30
  }
}
```

### 4. Get Recent Results
**GET** `/api/recent-results`

Response:
```json
{
  "success": true,
  "count": 10,
  "results": [
    {
      "id": 1,
      "filename": "test.jpg",
      "file_type": "image",
      "prediction": "FAKE",
      "confidence": 89.45,
      "timestamp": "2024-10-22T12:34:56"
    }
  ]
}
```

## Frontend Integration Example

### Using JavaScript Fetch:
```javascript
// Upload file for detection
async function detectDeepfake(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/detect-deepfake', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  return result;
}

// Usage
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];
const result = await detectDeepfake(file);
console.log(result);
```

### Using Axios:
```javascript
import axios from 'axios';

const formData = new FormData();
formData.append('file', file);

const response = await axios.post(
  'http://localhost:5000/detect-deepfake',
  formData,
  {
    headers: { 'Content-Type': 'multipart/form-data' }
  }
);

console.log(response.data);
```

## Testing the API

### Using curl:
```bash
# Test image
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/detect-deepfake

# Test video
curl -X POST -F "file=@test_video.mp4" http://localhost:5000/detect-deepfake

# Get stats
curl http://localhost:5000/api/stats
```

## Notes for Frontend Team:
1. Server must be running on port 5000
2. Maximum file size: 50MB
3. Processing time: 2-5 seconds for images, 10-30 seconds for videos
4. CORS is enabled - frontend can call from any origin