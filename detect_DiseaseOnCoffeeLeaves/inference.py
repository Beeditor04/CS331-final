from ultralytics import YOLO
import cv2
import yaml
def detect_leaf_disease(image_path,
                        model_path='./weights/best.pt'
                        ):
    """
    Nhận diện bệnh lá cà phê từ một ảnh đầu vào sử dụng mô hình YOLO đã huấn luyện.

    Params:
        image_path (str): Đường dẫn ảnh cần nhận diện.
        model_path (str): Đường dẫn model YOLO (.pt).
        yaml_path (str): Đường dẫn file YAML chứa class names.

    Returns:
        result_image (np.ndarray): Ảnh đã được vẽ kết quả.
    """

    # Gán màu cho từng class
    color_map = {
        'dom rong': (0, 0, 255),       # đỏ
        'nam ri sat': (0, 255, 0),     # xanh lá
        'phan trang': (255, 255, 0),   # vàng
        'sau ve bua': (255, 0, 0),     # xanh dương
    }

    # Load model YOLO
    model = YOLO(model_path)

    # Đọc ảnh và chuyển sang RGB
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Inference
    results = model(image_rgb)[0]
    label_dict = results.names

    # Vẽ kết quả lên ảnh gốc
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        class_name = label_dict[box.cls[0].item()]
        label = f"{class_name}: {conf:.2f}"

        # Chọn màu theo class
        color = color_map.get(class_name, (255, 255, 255))  # màu mặc định: trắng

        # Vẽ bounding box và nhãn
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2)

    return image  # Trả về ảnh kết quả (BGR)

def detect_leaf_disease_dict(image_path,
                        model_path='./weights/best.pt'
                        ):
    """
    Nhận diện bệnh lá cà phê từ một ảnh đầu vào sử dụng mô hình YOLO đã huấn luyện.

    Params:
        image_path (str): Đường dẫn ảnh cần nhận diện.
        model_path (str): Đường dẫn model YOLO (.pt).
        yaml_path (str): Đường dẫn file YAML chứa class names.

    Returns:
        dict: inference results containing bounding boxes and class labels.
    """
    # Load model YOLO
    model = YOLO(model_path)

    # Đọc ảnh và chuyển sang RGB
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Inference
    results = model(image_rgb)[0]

    # Predict with the model
    results = model(image_rgb)[0]  
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
    image_path = './sample/image_leaves.jpg'

    # Gọi hàm detect
    # result_dict = detect_leaf_disease_dict(image_path)
    result_image = detect_leaf_disease(image_path)
    # Hiển thị kết quả
    cv2.imshow('Coffee Leaf Disease Detection', result_image)
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close all windows
    # print(result_dict)
