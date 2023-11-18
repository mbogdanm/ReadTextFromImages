import os
import pandas as pd
import easyocr
import cv2
from tqdm import tqdm
import argparse
import re
from shapely.geometry import Polygon


# Function to draw bounding boxes and save the annotated image
def draw_bounding_boxes_and_save(image, results, image_file_path, annotated_images_folder):
    for result in results:
        bbox, text = result[:2]  # Get only the bounding box and text, ignore the score
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        text_position = (top_left[0], top_left[1] - 10 if top_left[1] - 10 > 0 else top_left[1] + 10)
        cv2.putText(image, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Create the Annotated Images folder if it doesn't exist
    if not os.path.exists(annotated_images_folder):
        os.makedirs(annotated_images_folder)

    # Save the annotated image inside the Annotated Images folder
    base_image_name = os.path.basename(image_file_path)
    annotated_image_path = os.path.join(annotated_images_folder, base_image_name.replace('.png', '_annotated.png'))
    cv2.imwrite(annotated_image_path, image)
    return annotated_image_path

# # Function to expand coordinates by a given tolerance
# def expand_coordinates(coordinates, tolerance=5):
#     x1, y1, x2, y2, x3, y3, x4, y4 = coordinates
#     # Expand the coordinates by the tolerance value
#     return (max(0, x1 - tolerance), max(0, y1 - tolerance),
#             x2 + tolerance, y2 - tolerance,
#             x3 + tolerance, y3 + tolerance,
#             x4 - tolerance, y4 + tolerance)


# # Function to sanitize text by removing punctuation
# def sanitize_text(text):
#     ignored_characters = r'[.:;!? ]'
#     return re.sub(ignored_characters, '', text)

# Function to create HTML output from match results
def create_html_output(matches, output_html_file, image_folder):
    # Begin the HTML document
    html = ['<html><head><title>Text Verification Report</title></head><body>', '<h1>Text Verification Report</h1>',
            '<table border="1" style="width:100%">',
            '<tr><th>Image</th><th>Expected Text</th><th>Detected Text</th><th>Result</th></tr>']

    # Populate the table with match results
    for match in matches:
        result_text = "PASS" if match['Match'] else "FAIL"
        color = 'green' if match['Match'] else 'red'
        annotated_image_path = os.path.join(image_folder, match['ImageName'].replace('.png', '_annotated.png'))

        html.append(f'<tr>')
        html.append(f'<td><a href="{annotated_image_path}" target="_blank">{match["ImageName"]}</a></td>')
        html.append(f'<td>{match["ExpectedText"]}</td>')
        html.append(f'<td>{match["DetectedText"]}</td>')
        html.append(f'<td><b style="color:{color};">{result_text}</b></td>')
        html.append(f'</tr>')

    # End the HTML document
    html.append('</table>')
    html.append('</body></html>')

    # Write the HTML content to a file
    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(''.join(html))



# Function to verify text in images
def verify_text_in_images(excel_path, image_path, output_html_file, annotated_images_folder):
    df = pd.read_excel(excel_path)
    reader = easyocr.Reader(['es'], gpu=False)
    matches = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Verifying Images"):
        image_name = row['Image Name']
        # Convert the expected text to string to prevent AttributeError
        expected_text = str(row['Text'])
        coordinates = tuple(map(int, re.findall(r'\d+', row['Coordinates'])))
        expected_polygon = Polygon([coordinates[i:i+2] for i in range(0, len(coordinates), 2)])

        image_file_path = os.path.join(image_path, image_name)
        img = cv2.imread(image_file_path)
        results = reader.readtext(img, detail=1, paragraph=False)
        draw_bounding_boxes_and_save(img, results, image_file_path, annotated_images_folder)

        # Initialize variables to store the best match within the coordinates
        best_score_within_coords = 0
        best_text_within_coords = None

        for (bbox, text, score) in results:
            detected_polygon = Polygon(bbox)
            if expected_polygon.contains(detected_polygon.centroid) and score > best_score_within_coords:
                # This text is within the coordinates and has a better score than previous finds
                best_score_within_coords = score
                best_text_within_coords = text

        # Check if we found any text within the coordinates
        if best_text_within_coords:
            # Convert both texts to string and lowercase to ensure proper comparison
            match_success = best_text_within_coords.lower() == expected_text.lower()
            matches.append({
                'Match': match_success,
                'ExpectedText': expected_text,
                'DetectedText': best_text_within_coords if match_success else best_text_within_coords,
                'ImageName': image_name
            })
        else:
            # No text found at all within the coordinates
            matches.append({
                'Match': False,
                'ExpectedText': expected_text,
                'DetectedText': "No text detected at specified coordinates",
                'ImageName': image_name
            })

        create_html_output(matches, output_html_file, image_path)
# Inside your main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify text in images.')
    parser.add_argument('excel_path', type=str, help='Path to the Excel file')
    parser.add_argument('image_path', type=str, help='Path to the directory containing images')
    parser.add_argument('output_text_file', type=str, help='Output file to write the results to')
    parser.add_argument('--annotated_folder_name', type=str, default='Annotated Images', help='Name of the folder to save annotated images')

    args = parser.parse_args()

    # Create the Annotated Images folder within image_path
    annotated_images_folder = os.path.join(args.image_path, args.annotated_folder_name)
    if not os.path.exists(annotated_images_folder):
        os.makedirs(annotated_images_folder)

    # Adjust the output file name for HTML format
    output_html_file = args.output_text_file if args.output_text_file.endswith('.html') else args.output_text_file.rsplit('.', 1)[0] + '.html'
    verify_text_in_images(args.excel_path, args.image_path, output_html_file, annotated_images_folder)

