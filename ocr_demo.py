import easyocr
import torch
import cv2
import numpy as np
import json

def read_receipt(reader, image_path):
    result = reader.readtext(image_path, output_format="json")

    image = cv2.imread(image_path)

    boxes = list()
    texts = list()
    confidents = list()

    for field in result:
        boxes.append(json.loads(field)["boxes"])
        texts.append(json.loads(field)["text"])
        confidents.append(float(json.loads(field)["confident"]))

    for box, text, confident in zip(boxes, texts, confidents):
        pts = np.array(box, dtype=np.int32)

        cv2.polylines(image, [pts], True, (0, 255, 0), 2)

        x, y = pts[0]
        cv2.putText(image, f"{text}({confident:.2f})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

    cv2.imwrite(f"{image_path}_output.png", image)


if __name__ == '__main__':
    print("Receipt Reader Started")

    reader = easyocr.Reader(['en', 'it'])

    read_receipt(reader, "test_receipt.jpg")

    print(f"Detecting & Reading using pipeline")

    img = cv2.imread("test_receipt.jpg")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast
    gray = cv2.equalizeHist(gray)

    # Denoise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Binarize (very important for OCR)
    _, thresh = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.imwrite("gray.png", gray)

    image = cv2.imread("gray.png")

    read_receipt(reader, "gray.png")

