import os
import pandas as pd
import easyocr
import cv2
from tqdm import tqdm
import argparse

# Function to verify text in images
def verify_text_in_images(excel_path, image_path, output_text_file):
    # Load the Excel file
    df = pd.read_excel(excel_path)

    # Initialize the reader for English (assuming 'en' for English)
    reader = easyocr.Reader(['en'], gpu=False)

    with open(output_text_file, 'w', encoding='utf-8') as output_file:
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Verifying Images"):
            image_name = row['Image Name']
            expected_text = row['Text']

            # Clean up and split coordinates
            coordinates_str = row['Coordinates']
            coordinates_str = coordinates_str.replace("(", "").replace(")", "").replace(" ", "")  # Remove spaces and parentheses
            coordinates = tuple(map(int, coordinates_str.split(',')))

            # Construct the full image path
            image_file_path = os.path.join(image_path, image_name)

            # Load the image
            img = cv2.imread(image_file_path)

            # Read text from the image
            results = reader.readtext(img, detail=1, paragraph=False)

            output_file.write(f"Image: {image_name}\n")

            found = False

            for (bbox, text, _) in results:
                bbox_coordinates = tuple(map(int, bbox[0][:2]))  # Extract (x, y) from the bbox
                if all(c1 <= c2 <= c3 for c1, c2, c3 in zip(coordinates, bbox_coordinates, coordinates)):
                    output_file.write(f"Coordinates: {coordinates}\n")
                    output_file.write(f"Expected Text: {expected_text}\n")
                    output_file.write(f"Actual Text: {text}\n")
                    if text == expected_text:
                        result = f"Text matches the expected text: {expected_text}\n"
                    else:
                        result = f"Text does not match the expected text: {expected_text}\n"
                    output_file.write(result)
                    found = True
                    break

            if not found:
                output_file.write("Coordinates: {} not found for this image.\n".format(coordinates))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify text in images.')
    parser.add_argument('excel_path', type=str, help='Path to the Excel file')
    parser.add_argument('image_path', type=str, help='Path to the directory containing images')
    parser.add_argument('output_text_file', type=str, help='Output file to write the results to')

    args = parser.parse_args()

    verify_text_in_images(args.excel_path, args.image_path, args.output_text_file)
