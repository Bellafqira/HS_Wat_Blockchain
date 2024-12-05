# Reversible Image Watermarking with Blockchain Integration

A Python implementation of a reversible watermarking scheme based on histogram shifting and prediction errors, with blockchain-based transaction logging. The system supports both standard images and DICOM medical images.

This project extends the watermarking scheme from [histogram_shiffting_predictions](https://github.com/Bellafqira/histogram_shiffting_predictions/tree/master) by adding blockchain integration for secure transaction logging and verification.

## Features

- **Reversible Watermarking**: Embed and extract watermarks without permanent image modification
- **Blockchain Integration**: Track and verify all watermarking operations
- **Batch Processing**: Handle multiple images efficiently
- **Support for Multiple Formats**: Works with common image formats (.jpg, .jpeg, .png, .bmp, .tiff) and DICOM (.dcm)
- **Configurable Parameters**: Customize embedding strength, kernel size, and other parameters
- **Quality Metrics**: Built-in BER (Bit Error Rate) and PSNR (Peak Signal-to-Noise Ratio) calculations

## Requirements

- Python 3.7+
- numpy
- pillow
- pydicom (for DICOM support)
- tqdm (for progress bars)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Configuration Generation

Use the `ConfigGenerator` class to create necessary configurations:

```python
from configs.gen_wat_cfs import ConfigGenerator

config_gen = ConfigGenerator()

# Generate embedding configuration
embed_config = config_gen.generate_embed_config(
    data_path="database/images",
    save_path="results/watermarked_images",
    message="WATERMARK_MESSAGE",
    blockchain_path="blockchain/database/blockchainDB.json",
    data_type="dcm"  # or "jpg", "png", etc.
)
```

### Watermark Embedding

```python
from watermarking.watermark_embedder_batch import BatchEmbedderProcessor

# Initialize processor with config
processor = BatchEmbedderProcessor(embed_config)

# Process images
result = processor.process_images()
```

### Watermark Extraction

```python
from watermarking.watermark_extractor import WatermarkExtractor

# Initialize extractor with config
extractor = WatermarkExtractor(extract_config)

# Extract watermark
result = extractor.extract()
```

### Watermark Removal

```python
from watermarking.watermark_remover_batch import BatchRemoveProcessor

# Initialize processor with config
processor = BatchRemoveProcessor(remove_config)

# Process images
result = processor.process_images()
```

## Configuration Options

### Embedding Configuration

- `data_path`: Path to input images
- `save_path`: Path for watermarked images
- `message`: Watermark message
- `blockchain_path`: Path to blockchain database
- `kernel`: Prediction kernel (default: [[0, 1/4, 0], [1/4, 0, 1/4], [0, 1/4, 0]])
- `stride`: Kernel stride (default: 3)
- `t_hi`: Threshold high value (default: 0)
- `bit_depth`: Image bit depth (default: 16 for DICOM, 8 for others)

### Extraction/Removal Configuration

- `data_path`: Path to watermarked images
- `save_path`: Path for recovered images
- `ext_wat_path`: Path for extracted watermarks
- `blockchain_path`: Path to blockchain database


## Watermarking Process Overview

The watermarking scheme is based on histogram shifting of prediction errors with overflow management. Here's how it works:

1. **Watermark Generation**:
   - A message string is combined with a secret key
   - SHA256 is used to generate a 256-bit watermark
   - The secret key generates a random sequence to determine watermarkable regions

2. **Embedding Process**:
   - For each image region where random sequence bit = 1:
     - Apply prediction kernel to calculate neighbors' average
     - Calculate error between center pixel and prediction
     - If error ≥ 0, modify the pixel value using histogram shifting
     - Handle overflow cases for pixel values near maximum

3. **Extraction Process**:
   - Use secret key to regenerate random sequence
   - For each marked region:
     - Recalculate prediction error
     - Extract watermark bits from modified error values
     - Restore original pixel values
   - Handle overflow cases using stored positions

## Blockchain Integration

Our system uses a blockchain to track both watermark embedding and removal operations - a novel approach in the field. Each block contains:

### Embedding Block Example:
```json
{
  "header": {
    "timestamp": 1732734615.216023,
    "previous_hash": "72b2c66ea79b...",
    "block_number": 12
  },
  "info": "embedder",
  "transaction": {
    "total_images": 2,
    "processed_images": 2,
    "failed_images": [],
    "transaction_dict": {
      "9c8a15d306a28...": {
        "timestamp": "1732734615.179847",
        "secret_key": "9dd4d991c251...",
        "message": "ID_Paroma_Med",
        "watermark": "5d99700ef982...",
        "kernel": [[0, 0.25, 0], [0.25, 0, 0.25], [0, 0.25, 0]],
        "stride": 3,
        "t_hi": 0,
        "hash_image_wat": "9c8a15d306a28...",
        "hash_image_orig": "59fc674587589...",
        "bit_depth": 16,
        "data_type": "dcm",
        "operation_type": "embedding"
      }
    }
  }
}
```

### Removal Block Example:
```json
{
  "header": {
    "timestamp": 1732734638.984186,
    "previous_hash": "67dcdfbbf692...",
    "block_number": 13
  },
  "info": "remover",
  "transaction": {
    "timestamp": "1732734638.984186",
    "operation": "remove",
    "batch_size": 2,
    "successful_extractions": 2,
    "failed_extractions": 0,
    "average_ber": 0.0,
    "transaction_dict": {
      "9c8a15d306a28...": {
        "operation_type": "removal",
        "original_image_hash": "59fc674587589...",
        "watermarked_image_hash": "9c8a15d306a28...",
        "recovered_image_hash": "59fc674587589...",
        "extraction_ber": 0.0,
        "original_watermark": "5d99700ef982...",
        "extracted_watermark": "5d99700ef982...",
        "removal_parameters": {
          "kernel": [[0, 0.25, 0], [0.25, 0, 0.25], [0, 0.25, 0]],
          "stride": 3,
          "t_hi": 0,
          "bit_depth": 16
        }
      }
    }
  }
}
```

## Extraction vs Removal Operations

### Extraction (test_extractor)
- Used to verify potentially modified images
- Works even when image hash doesn't match blockchain records
- Extracts and compares watermark content to identify original block
- Useful for detecting and tracing modified images

### Removal (test_remover_batch)
- Requires exact image hash match in blockchain
- Completely reverses watermarking process
- Recovers original image
- Creates new blockchain block to track removal operation
- Maintains complete audit trail of image modifications

## Innovation and Future Work

This implementation introduces a novel approach by tracking both embedding and removal operations in the blockchain. Future improvements will include:

- Block signature implementation for enhanced security
- Encryption of sensitive data (secret keys, messages)
- Enhanced verification mechanisms
- Improved scalability for large image datasets

These security enhancements will further strengthen the system's ability to protect and track image authenticity while maintaining the reversibility of the watermarking process.


## Docker Setup

### Prerequisites
- Docker installed on your system
- Docker Compose installed on your system

### Building the Docker Image

1. Create a Dockerfile in the project root:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p database/images results blockchain/database configs/database

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build the image:
```bash
docker build -t watermarking-api .
```

### Running with Docker Compose

1. Use the existing docker-compose.yml file:
```yaml
version: '3.8'

services:
  watermarking-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database/images:/app/database/images
      - ./results:/app/results
      - ./blockchain/database:/app/blockchain/database
      - ./configs/database:/app/configs/database
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

2. Start the service:
```bash
docker-compose up -d
```

## Testing the Docker Container

### 1. Basic Health Check
```bash
curl http://localhost:8000/health
```

### 2. Testing Embedding
```bash
curl -X POST http://localhost:8000/api/watermark/embed \
  -H "Content-Type: application/json" \
  -d '{
    "data_path": "/app/database/images/test.dcm",
    "save_path": "/app/results/watermarked.dcm",
    "message": "test_watermark",
    "data_type": "dcm"
  }'
```

### 3. Testing Extraction
```bash
curl -X POST http://localhost:8000/api/watermark/extract \
  -H "Content-Type: application/json" \
  -d '{
    "data_path": "/app/results/watermarked.dcm",
    "data_type": "dcm"
  }'
```

### 4. Testing Removal
```bash
curl -X POST http://localhost:8000/api/watermark/remove \
  -H "Content-Type: application/json" \
  -d '{
    "data_path": "/app/results/watermarked.dcm",
    "save_path": "/app/results/recovered.dcm",
    "ext_wat_path": "/app/results/watermark.npy",
    "data_type": "dcm"
  }'
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## Questions and Contact

If you have any questions or need assistance, please contact:
- Reda Bellafqira (reda.bellafqira@imt-atlantique.fr)

## License

MIT License - See LICENSE file for details

## References

1. Sun, Y., et al. (2023). FRRW: A feature extraction-based robust and reversible watermarking scheme utilizing zernike moments and histogram shifting.
2. Naskar, R., & Subhra Chakraborty, R. (2013). Histogram‐bin‐shifting‐based reversible watermarking for colour images.
3. [histogram_shiffting_predictions](https://github.com/Bellafqira/histogram_shiffting_predictions/tree/master) - Original watermarking scheme implementation by Reda Bellafqira