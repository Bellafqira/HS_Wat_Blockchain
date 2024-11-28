import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
from datetime import datetime
from dataclasses import asdict, dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
from tqdm import tqdm

from PIL import Image
from watermarking.watermark_remover import WatermarkRemove
from blockchain.blockchain import Blockchain


@dataclass
class BatchExtractionResult:
    """Data class for batch extraction results"""
    total_images: int
    processed_images: int
    failed_images: List[str]
    successful_extractions: Dict[str, float]  # image_hash: BER
    processing_time: float
    average_ber: float


@dataclass
class BatchTransaction:
    """Data class for batch transaction"""
    timestamp: str
    operation: str = "remove"
    batch_size: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    average_ber: float = 0.5
    transaction_dict: Dict[str, dict] = None


class BatchRemoveProcessor:
    def __init__(self, config):
        self.logger = None
        self.config = config
        self.supported_formats: Set[str] = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.dcm'}
        self.blockchain = Blockchain(config.blockchain_path)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_image_files(self, directory: str) -> List[Path]:
        """Get all supported image files from directory recursively."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        image_files = []
        for ext in self.supported_formats:
            image_files.extend(directory_path.glob(f"*{ext}"))
            # image_files.extend(directory_path.rglob(f"*{ext.upper()}"))

        return sorted(set(image_files))  # Remove duplicates

    def process_single_image(self, img_path: Path, rec_path: Path, wat_path: Path) -> tuple:
        """Process a single image and return results."""
        try:
            # Update config for current image
            self.config.data_path = str(img_path)
            save_name = f"recovered_{img_path.name}"
            self.config.save_path = str(rec_path) + "/" + save_name
            self.config.ext_wat_path = str(wat_path) + '.npy'

            # Create extractor and process image
            extractor = WatermarkRemove(self.config)
            result = extractor.extract_and_remove()

            return (
                img_path,
                True,
                result.transaction,
                result.ber
            )

        except Exception as e:
            self.logger.error(f"Error processing {img_path.name}: {str(e)}")
            return img_path, False, None, None

    def process_images(self) -> BatchExtractionResult:
        """Process all images in the configured directory."""
        start_time = datetime.now()

        # Get all image files
        try:
            image_files = self.get_image_files(self.config.data_path)
            total_images = len(image_files)

            if not total_images:
                raise ValueError(f"No supported images found in {self.config.data_path}")

            self.logger.info(f"Starting batch processing of {total_images} images...")

            # Create save directory
            save_path = Path(self.config.save_path)
            ext_wat_path = Path(self.config.ext_wat_path)
            save_path.mkdir(parents=True, exist_ok=True)
            ext_wat_path.mkdir(parents=True, exist_ok=True)

            # Process images using thread pool
            successful_extractions = {}
            failed_images = []
            image_transactions = {}

            with ThreadPoolExecutor() as executor:
                # futures = [executor.submit(self.process_single_image, img_path)
                #            for img_path in image_files]

                futures = [self.process_single_image(img_path, save_path, ext_wat_path)
                           for img_path in image_files]

                # Process results with progress bar
                for future in tqdm(futures, total=len(futures), desc="Processing images"):
                    img_path, success, transaction, ber = future  # .result()

                    if success:
                        image_hash = transaction["watermarked_image_hash"]
                        successful_extractions[image_hash] = ber
                        image_transactions[image_hash] = transaction
                    else:
                        failed_images.append(str(img_path))

            # Calculate statistics
            processed_images = len(successful_extractions)
            average_ber = (sum(successful_extractions.values()) / processed_images
                           if processed_images > 0 else 0.0)

            # Create batch transaction
            batch_transaction = BatchTransaction(
                timestamp=str(datetime.now().timestamp()),
                batch_size=total_images,
                successful_extractions=processed_images,
                failed_extractions=len(failed_images),
                average_ber=average_ber,
                transaction_dict=image_transactions,
                operation="remove"
            )

            # # Add to blockchain
            new_block = self.blockchain.add_transaction(asdict(batch_transaction), info="remover")

            # Verify chain
            is_valid = self.blockchain.verify_chain()
            print(f"\nBlockchain is valid: {is_valid}")

            print(f"\nNew block created:")
            print(f"Block number: {new_block.header.block_number}")
            print(f"Block hash: {new_block.hash}")
            print(f"Timestamp: {datetime.fromtimestamp(new_block.header.timestamp)}")

            # Create result object
            processing_time = (datetime.now() - start_time).total_seconds()
            result = BatchExtractionResult(
                total_images=total_images,
                processed_images=processed_images,
                failed_images=failed_images,
                successful_extractions=successful_extractions,
                processing_time=processing_time,
                average_ber=average_ber
            )

            # # Log results
            # self.logger.info(f"\nBatch processing completed in {processing_time:.2f} seconds")
            # self.logger.info(f"Successfully processed: {processed_images}/{total_images} images")
            # self.logger.info(f"Average BER: {average_ber:.4f}")
            #
            # if failed_images:
            #     self.logger.warning(f"Failed to process {len(failed_images)} images")

            return result

        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            raise

