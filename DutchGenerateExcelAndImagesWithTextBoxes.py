import os
import cv2
import pandas as pd
from tqdm import tqdm
import easyocr

def extract_texts_and_coordinates(image_folder, language, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    excel_folder = os.path.join(output_folder, 'text_output')
    os.makedirs(excel_folder, exist_ok=True)

    reader = easyocr.Reader([language], gpu=False)
    all_results = []

    for image_filename in tqdm(os.listdir(image_folder)):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_filename)
            img = cv2.imread(image_path)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

            results = reader.readtext(gray_img, detail=1, paragraph=False)
            text_box_counter = 1

            for (bbox, text, _) in results:
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))

                # Ensure the text box number is within the image resolution
                text_location = (max(tl[0], 0), max(tl[1] - 10, 0))

                all_results.append((image_filename, text, (tl, tr, br, bl), text_box_counter))

                # Draw rectangle and text box number on the image
                cv2.rectangle(img, tl, br, (0, 255, 0), 2)
                cv2.putText(img, str(text_box_counter), text_location, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                text_box_counter += 1

            output_image_path = os.path.join(output_folder, f"boxed_{image_filename}")
            cv2.imwrite(output_image_path, img)

    return all_results, excel_folder

image_folder = r'C:\Users\MIHAL_B1\PycharmProjects\ReadText\images\nl'  # Change the path to your Chinese images folder
language = 'nl'  # Use 'ch_sim' for Simplified Chinese or 'ch_tra' for Traditional Chinese
output_folder = r'C:\Users\MIHAL_B1\PycharmProjects\ReadText\images\nl_output_images'  # Change the output path accordingly
results, excel_folder = extract_texts_and_coordinates(image_folder, language, output_folder)

df = pd.DataFrame(results, columns=['Image Name', 'Text', 'Coordinates', 'Text Box Number'])
excel_path = os.path.join(excel_folder, 'nl_results.xlsx')
df.to_excel(excel_path, index=False)
