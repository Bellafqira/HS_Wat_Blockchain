from configs.gen_wat_cfs import ConfigGenerator
from watermarking.watermark_remover_batch import BatchRemoveProcessor

# Example usage
if __name__ == "__main__":

    try:
        # Initialize config generator
        config_gen = ConfigGenerator()
        loaded_remove_config = config_gen.load_remove_config("remove_config")

        # Start processing
        processor = BatchRemoveProcessor(loaded_remove_config)
        result = processor.process_images()

        print("\nProcessing Summary:")
        print(f"Total images: {result.total_images}")
        print(f"Successfully processed: {result.processed_images}")
        print(f"Number of Failed images: {len(result.failed_images)}")
        print(f"Average BER: {result.average_ber:.4f}")
        print(f"Processing time: {result.processing_time} seconds")

    except Exception as e:
        print(f"Error during batch processing 55: {str(e)}")
