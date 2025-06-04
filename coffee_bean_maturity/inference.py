from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
import numpy as np
def detect_coffee_labels(img: np.ndarray) -> dict:
    """
    Perform inference on the input image to determine coffee bean maturity.

    Args:
        img (numpy.ndarray): Input image of the coffee beans.

    Returns:
        dict: Inference results containing bounding boxes and class labels
    """
    try:
        model = YOLO('./best.pt') 
    except Exception as e:
        model = YOLO('yolov8n.pt')  # Fallback to a default model if loading fails
    #? Note: for future, i don't fucking use ultralytics, goonna try sth else
    
    model.conf = 0.5

    # Predict with the model
    results = model(img)[0]  
    label_dict = results.names
    # construct results for llm 
    results_dict = {
        "boxes": [],
        "labels": []
    }
    for box in results.boxes:
        results_dict["boxes"].append({
            "x1": int(box.xyxy[0][0]),
            "y1": int(box.xyxy[0][1]),
            "x2": int(box.xyxy[0][2]),
            "y2": int(box.xyxy[0][3])
        })
        results_dict["labels"].append(label_dict[box.cls[0].item()])
    return results_dict

# run a sample
if __name__ == "__main__":
    imageUrl = './IMG_6583-1.jpg'
    # Load a model
    img = cv2.imread(imageUrl)
    results_dict = detect_coffee_labels(img)
    print(results_dict)
