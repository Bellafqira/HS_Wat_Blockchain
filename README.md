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

## Project Structure

```
├── blockchain/
│   └── blockchain.py          # Blockchain implementation
├── configs/
│   └── gen_wat_cfs.py        # Configuration generator
├── watermarking/
│   ├── watermark_embedder.py  # Single image embedder
│   ├── watermark_extractor.py # Watermark extraction
│   └── watermark_remover.py   # Watermark removal
├── utils/
│   └── utils.py              # Utility functions
└── tests/                    # Test cases
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

## Blockchain Integration

The system uses a simple blockchain to store:
- Embedding transactions
- Extraction results
- Removal operations
- Image hashes and timestamps

Each operation creates a new block with:
- Transaction details
- Timestamps
- Operation parameters
- Quality metrics

## Error Handling

The system includes comprehensive error handling for:
- Invalid configurations
- File I/O errors
- Image format issues
- Blockchain verification failures

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