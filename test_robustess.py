import numpy as np
from PIL import Image
import cv2
from scipy import ndimage
from typing import Tuple

from configs.gen_wat_cfs import ConfigGenerator
from watermarking.watermark_extractor import WatermarkExtractor


class WatermarkAttacks:
    @staticmethod
    def histogram_shifting(image: np.ndarray, shift_value: int) -> np.ndarray:
        """
        Apply histogram shifting attack by adding a constant value to all pixels.

        Args:
            image: Input image as numpy array
            shift_value: Integer value to shift the histogram

        Returns:
            Attacked image with shifted histogram
        """
        shifted = image.astype(np.float32).copy() + shift_value
        # shifted[:10,:10] = 255
        # Clip values to valid range [0, 255]
        return np.clip(shifted, 0, 255).astype(np.uint8)

    @staticmethod
    def contrast_adjustment(image: np.ndarray, alpha: float = 1.5) -> np.ndarray:
        """
        Adjust image contrast by multiplying pixel values by alpha.

        Args:
            image: Input image as numpy array
            alpha: Contrast factor (>1 increases contrast, <1 decreases contrast)

        Returns:
            Contrast-adjusted image
        """
        adjusted = image.astype(np.float32) * alpha
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    @staticmethod
    def gamma_correction(image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
        """
        Apply gamma correction to the image.

        Args:
            image: Input image as numpy array
            gamma: Gamma value for correction

        Returns:
            Gamma-corrected image
        """
        # Normalize to 0-1 range
        normalized = image.astype(np.float32) / 255.0
        # Apply gamma correction
        corrected = np.power(normalized, gamma)
        # Scale back to 0-255 range
        return np.clip(corrected * 255.0, 0, 255).astype(np.uint8)

    @staticmethod
    def histogram_equalization(image: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization to enhance image contrast.

        Args:
            image: Input image as numpy array

        Returns:
            Histogram-equalized image
        """
        return cv2.equalizeHist(image.astype(np.uint8))

    @staticmethod
    def adaptive_histogram_equalization(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """
        Apply adaptive histogram equalization using CLAHE.

        Args:
            image: Input image as numpy array
            clip_limit: Threshold for contrast limiting

        Returns:
            CLAHE-processed image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        return clahe.apply(image.astype(np.uint8))

    @staticmethod
    def jpeg_compression(image: np.ndarray, quality: int = 50) -> np.ndarray:
        """
        Apply JPEG compression and decompression while maintaining original size.

        Args:
            image: Input image as numpy array
            quality: JPEG quality factor (0-100, lower means more compression)

        Returns:
            Compressed and decompressed image
        """
        # Create a temporary PIL Image
        img_pil = Image.fromarray(image)

        # Save with JPEG compression to bytes buffer
        import io
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        # Read back the compressed image
        compressed_img = Image.open(buffer)
        compressed_array = np.array(compressed_img)

        # Ensure we maintain the original size
        if compressed_array.shape != image.shape:
            compressed_img = compressed_img.resize(
                (image.shape[1], image.shape[0]),
                Image.LANCZOS
            )
            compressed_array = np.array(compressed_img)

        return compressed_array

    @staticmethod
    def gaussian_noise(image: np.ndarray, mean: float = 0, std: float = 25) -> np.ndarray:
        """
        Add Gaussian noise to the image.

        Args:
            image: Input image as numpy array
            mean: Mean of the Gaussian distribution
            std: Standard deviation of the Gaussian distribution

        Returns:
            Noisy image
        """
        noise = np.random.normal(mean, std, image.shape)
        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)


def test_watermark_robustness(original_image: np.ndarray, watermark_extractor, config) -> dict:
    """
    Test watermark robustness against various attacks.

    Args:
        original_image: Original watermarked image
        watermark_extractor: Function to extract watermark
        config: Configuration dictionary for watermark extraction

    Returns:
        Dictionary containing extracted watermarks and PSNR values for each attack
    """
    attacks = WatermarkAttacks()
    results = {}

    # Test different attacks
    test_cases = {
        'histogram_shift_+10': lambda img: attacks.histogram_shifting(img, 10),
        # 'histogram_shift_-10': lambda img: attacks.histogram_shifting(img, 0),
        'contrast_increase': lambda img: attacks.contrast_adjustment(img, 1.5),
        'contrast_decrease': lambda img: attacks.contrast_adjustment(img, 0.7),
        'gamma_correction': lambda img: attacks.gamma_correction(img, 2.2),
        'hist_equalization': lambda img: attacks.histogram_equalization(img),
        'adaptive_hist_eq': lambda img: attacks.adaptive_histogram_equalization(img),
        'gaussian_noise': lambda img: attacks.gaussian_noise(img, 0, 1),
        'jpeg_compression_high': lambda img: attacks.jpeg_compression(img, 98),
        # 'jpeg_compression_medium': lambda img: attacks.jpeg_compression(img, 50),
        # 'jpeg_compression_low': lambda img: attacks.jpeg_compression(img, 20)
    }

    config.data_path = "attacked.png"

    for attack_name, attack_func in test_cases.items():
        # Apply attack
        attacked_image = attack_func(original_image.copy())
        # save in file
        attacked_image = Image.fromarray(np.uint8(attacked_image))

        attacked_image.save(config.data_path)
        # Extract watermark from attacked image
        try:
            extractor = watermark_extractor(config)
            result01 = extractor.extract()

            results[attack_name] = {
                'extracted_watermark': result01,
                'psnr': 0
            }
        except Exception as e:
            results[attack_name] = {
                'error': str(e)
            }

    return results


def calculate_psnr(original: np.ndarray, modified: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio between two images.
    """
    mse = np.mean((original - modified) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


# Example usage:
if __name__ == "__main__":

    config_gen = ConfigGenerator()
    config_gen.generate_extract_config(data_path="results/watermarked_images/images_png/watermarked_Normal01.png",
                                       blockchain_path="blockchain/database/blockchainDB.json", data_type="png",
                                       filename= "extract_config")
    loaded_extract_config = config_gen.load_extract_config("extract_config")

    # Start the extraction process
    extractor = WatermarkExtractor(loaded_extract_config)
    result01 = extractor.extract()
    print(result01)

    # Read test image
    image_orig = Image.open("results/watermarked_images/images_png/watermarked_Normal01.png").convert('L')
    watermarked_image = np.array(image_orig)

    print("image size", watermarked_image.shape)

    # Test robustness
    results = test_watermark_robustness(watermarked_image, WatermarkExtractor, loaded_extract_config)

    # Print results
    for attack_name, result in results.items():
        print(f"\nResults for {attack_name}:")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            if result['extracted_watermark'] is not None:
                print(f"results: {result['extracted_watermark']}")


    # # Configure watermark parameters
    # config = {
    #     "bit_depth": 8,
    #     "t_hi": 0,
    #     "stride": 3,
    #     "kernel": np.array([[0, 1 / 4, 0],
    #                         [1 / 4, 0, 1 / 4],
    #                         [0, 1 / 4, 0]]),
    #
    # }
    #
    # # Create watermarked image (using your existing code)
    # from watermarking.watermark_extractor import WatermarkExtractor
    #
    # embedder = WatermarkEmbedder(config)
    # watermarked_image = embedder.embed_watermarks(image_np)
    #
    # READ IMAGE

    # Test robustness
    # results = test_watermark_robustness(watermarked_image, extract_watermark, config)
    #
    # # Print results
    # for attack_name, result in results.items():
    #     print(f"\nResults for {attack_name}:")
    #     if 'error' in result:
    #         print(f"Error: {result['error']}")
    #     else:
    #         print(f"PSNR: {result['psnr']:.2f} dB")
    #         if result['extracted_watermark'] is not None:
    #             print(f"Extracted watermark length: {len(result['extracted_watermark'])}")