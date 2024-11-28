# Example usage
from dataclasses import dataclass

from configs.gen_wat_cfs import ConfigGenerator
from watermarking.watermark_embedder_batch import BatchEmbedderProcessor

if __name__ == "__main__":

    try:
        # Initialize config generator
        config_gen = ConfigGenerator()
        loaded_embed_config = config_gen.load_embed_config("embed_config")

        # Create processor and process images
        processor = BatchEmbedderProcessor(loaded_embed_config)
        result = processor.process_images()

        print("\nProcessing Summary:")
        print(f"Total images: {result.total_images}")
        print(f"Successfully processed: {result.processed_images}")
        print(f"Failed images: {len(result.failed_images)}")
        print(f"Processing time: {result.processing_time:.2f} seconds")

        # Access transaction dictionary
        for image_hash, transaction in result.transaction_dict.items():
            print(f"\nTransaction for image hash: {image_hash[:16]}...")
            print(f"Timestamp: {transaction['timestamp']}")
            print(f"Original image hash: {transaction['hash_image_orig'][:16]}...")
            print(f"Secret key: {transaction['secret_key'][:16]}...")
            print(f"kernel: {transaction['kernel']}...")

    except Exception as e:
        print(f"Error during batch processing: {str(e)}")
