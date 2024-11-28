import os
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
from dataclasses import asdict, dataclass
from PIL import Image

from blockchain.blockchain import Blockchain
from watermarking.watermark_embedder import WatermarkEmbedder


@dataclass
class BatchProcessingResult:
    """Data class for batch processing results"""
    total_images: int
    processed_images: int
    failed_images: List[str]
    transaction_dict: Dict[str, dict]
    processing_time: float


class BatchEmbedderProcessor:
    def __init__(self, config):
        self.config = config
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.dcm'}
        self.embedder = WatermarkEmbedder(config)
        self.transaction_dict = {}
        self.blockchain = Blockchain(config.blockchain_path)

    def get_image_files(self, directory: str) -> List[Path]:
        """
        Get all supported image files from directory.

        Args:
            directory: Directory path to scan for images

        Returns:
            List of Path objects for valid image files
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        image_files = []
        for ext in self.supported_formats:
            image_files.extend(directory_path.glob(f"*{ext}"))

        return sorted(image_files)

    def process_images(self) -> BatchProcessingResult:
        """
        Process all images in the configured directory.

        Returns:
            BatchProcessingResult with processing statistics and transaction dictionary
        """
        start_time = datetime.now()

        # Get all image files
        try:
            image_files = self.get_image_files(self.config.data_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error accessing image directory: {str(e)}")

        if not image_files:
            raise ValueError(f"No supported images found in {self.config.data_path}")

        total_images = len(image_files)
        processed_images = 0
        failed_images = []

        # Create save directory if it doesn't exist
        save_path = Path(self.config.save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        print(f"Starting batch processing of {total_images} images...")

        # Process each image
        for img_path in image_files:
            try:
                # if not self.verify_image(img_path):
                #     print(f"Skipping invalid image: {img_path.name}")
                #     failed_images.append(str(img_path))
                #     continue

                print(f"\nProcessing image: {img_path.name}")

                # Update config with current image paths
                self.config.data_path = str(img_path)
                self.config.save_path = str(save_path / f"watermarked_{img_path.name}")

                # Embed watermark
                transaction = self.embedder.embed_watermarks()

                # Store transaction in dictionary using watermarked image hash as key
                self.transaction_dict[transaction.hash_image_wat] = asdict(transaction)

                processed_images += 1
                print(f"Successfully processed: {img_path.name}")

            except Exception as e:
                print(f"Error processing {img_path.name}: {str(e)}")
                failed_images.append(str(img_path))

        processing_time = (datetime.now() - start_time).total_seconds()

        # Create result object
        result = BatchProcessingResult(
            total_images=total_images,
            processed_images=processed_images,
            failed_images=failed_images,
            transaction_dict=self.transaction_dict,
            processing_time=processing_time
        )

        # # Save transaction dictionary in the blockchain
        # Add transaction
        new_block = self.blockchain.add_transaction(asdict(result), info="embedder")

        print(f"\nNew block created:")
        print(f"Block number: {new_block.header.block_number}")
        print(f"Block hash: {new_block.hash}")
        print(f"Timestamp: {datetime.fromtimestamp(new_block.header.timestamp)}")

        print(f"\nBatch processing completed in {processing_time:.2f} seconds")
        print(f"Successfully processed: {processed_images}/{total_images} images")
        if failed_images:
            print(f"Failed to process {len(failed_images)} images")

        return result
