import os
import easyocr
import cv2
from tqdm import tqdm

def extract_texts_and_coordinates(image_folder, language):
    # Initialize the reader with the specified language
    reader = easyocr.Reader([language], gpu=False)

    # Create a list to store the text, coordinates, and rectangle numbers for all images
    all_results = []

    for image_filename in tqdm(os.listdir(image_folder)):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_filename)
            img = cv2.imread(image_path)

            results = reader.readtext(img, detail=1, paragraph=False)

            text_box_counter = 1  # Initialize the text box number

            for (bbox, text, _) in results:
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))

                all_results.append((image_filename, text, (tl, tr, br, bl), text_box_counter))

                text_box_counter += 1  # Increment the text box number

    return all_results

# Example usage
image_folder = r'C:\Users\MIHAL_B1\PycharmProjects\ReadText\images'
language = 'ar'
results = extract_texts_and_coordinates(image_folder, language)

# Write the results to a text file with UTF-8 encoding to handle non-ASCII characters
with open('output.txt', 'w', encoding='utf-8') as file:
    for image_filename, text, coords, text_box_number in results:
        file.write(f"Image: {image_filename}, Text: {text}, Coordinates: {coords}, Text Box Number: {text_box_number}\n")

# Print the results to the console
for image_filename, text, coords, text_box_number in results:
    print(f"Image: {image_filename}, Text: {text}, Coordinates: {coords}, Text Box Number: {text_box_number}")
