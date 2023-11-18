# Import necessary libraries
import easyocr
import cv2


# Function to check text in an image
def check_text_in_image(coordinates, expected_text, language):
    # Initialize the reader with the specified language
    reader = easyocr.Reader([language], gpu=False)

    # Load the image you want to analyze
    img = cv2.imread('images/Arabic_AAR_01.png')

    # Read text from the image
    results = reader.readtext(img, detail=1, paragraph=False)

    # Create a list to store the text, coordinates, and scores
    text_and_coords = []

    # Loop through the results
    for (bbox, text, prob) in results:
        # Define bounding boxes (tl, tr, br, bl)
        (tl, tr, br, bl) = bbox

        # Convert coordinates to integers
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        # Check if the bounding box coordinates match the specified coordinates
        if tl[0] >= coordinates[0] and tl[1] >= coordinates[1] and br[0] <= coordinates[2] and br[1] <= coordinates[3]:
            # Extract the text at the specified coordinates
            extracted_text = text

            # Compare the extracted text with the expected text
            if extracted_text == expected_text:
                result = f"Text at specified coordinates matches expected text! (Score: {prob})"
            else:
                result = f"Text at specified coordinates does not match expected text. Expected text was: {expected_text} \n(Score: {prob})"

            # Add the text, coordinates, and result to the list
            text_and_coords.append((extracted_text, (tl, tr, br, bl), result))

    return text_and_coords  # Return the list of results


# Example usage
coordinates = (375, 189, 759, 225)
expected_text = 'تشغيل نظام '
language = 'ar'
results = check_text_in_image(coordinates, expected_text, language)

# Open a file for writing with UTF-8 encoding to handle non-ASCII characters
with open('output.txt', 'w', encoding='utf-8') as file:
    for text, coords, result in results:
        file.write(f"Text: {text},\nCoordinates: {coords},\nResult: {result}")

# Print the result to the console
for text, coords, result in results:
    print(f"Text: {text},\nCoordinates: {coords},\nResult: {result}")
