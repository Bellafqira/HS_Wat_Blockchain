from configs.gen_wat_cfs import ConfigGenerator
from watermarking.watermark_extractor import WatermarkExtractor

# Example usage
if __name__ == "__main__":

    try:

        # Initialize config generator
        config_gen = ConfigGenerator()
        loaded_extract_config = config_gen.load_extract_config("extract_config")

        # Start the extraction process
        extractor = WatermarkExtractor(loaded_extract_config)
        result = extractor.extract()

        print(result)

    except Exception as e:
        print(f"Error during extraction: {str(e)}")

