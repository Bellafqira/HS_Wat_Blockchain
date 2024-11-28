import json

from configs.gen_wat_cfs import ConfigGenerator


# Example usage
def main():
    # Initialize config generator
    config_gen = ConfigGenerator()

    try:
        # Generate embedding configuration
        embed_config = config_gen.generate_embed_config(
            data_path="database/images_dcm",
            save_path="results/watermarked_images/images_dcm",
            message="ID_Paroma_Med",
            blockchain_path="blockchain/database/blockchainDB.json",
            data_type="dcm"
        )
        print("Generated embedding configuration:")
        print(json.dumps(embed_config.__dict__, indent=2))

        # Generate extraction configuration
        extract_config = config_gen.generate_extract_config(
            data_path="database/images_dcm/CT000000.dcm",
            blockchain_path="blockchain/database/blockchainDB.json",
            data_type="dcm"
        )
        print("\nGenerated extraction configuration:")
        print(json.dumps(extract_config.__dict__, indent=2))

        # Generate removal configuration
        remove_config = config_gen.generate_remove_config(
            data_path="results/watermarked_images/images_dcm",
            save_path="results/recovered_images/images_dcm",
            ext_wat_path="results/recovered_watermark/images_dcm",
            blockchain_path="blockchain/database/blockchainDB.json",
            data_type="dcm"
        )
        print("\nGenerated removal configuration:")
        print(json.dumps(remove_config.__dict__, indent=2))

        # Load and verify configurations
        loaded_embed_config = config_gen.load_embed_config()
        loaded_extract_config = config_gen.load_extract_config()
        loaded_remove_config = config_gen.load_remove_config()

        print("\nConfigurations loaded successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()