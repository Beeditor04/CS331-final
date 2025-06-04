from ultralytics import YOLO
import cv2
import yaml

def detect_leaf_disease(image_path,
                        model_path='./detect_DiseaseOnCoffeeLeaves/weights/best.pt',
                        yaml_path='./detect_DiseaseOnCoffeeLeaves/data.yaml'):
    """
    Nhận diện bệnh lá cà phê từ một ảnh đầu vào sử dụng mô hình YOLO đã huấn luyện.

    Params:
        image_path (str): Đường dẫn ảnh cần nhận diện.
        model_path (str): Đường dẫn model YOLO (.pt).
        yaml_path (str): Đường dẫn file YAML chứa class names.

    Returns:
        result_image (np.ndarray): Ảnh đã được vẽ kết quả.
    """
    # Load class names từ YAML
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    class_names = data['names']

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

    # Vẽ kết quả lên ảnh gốc
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        class_name = class_names[cls]
        label = f"{class_name}: {conf:.2f}"

        # Chọn màu theo class
        color = color_map.get(class_name, (255, 255, 255))  # màu mặc định: trắng

        # Vẽ bounding box và nhãn
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2)

    return image  # Trả về ảnh kết quả (BGR)

# run a sample
if __name__ == "__main__":
    image_path = './detect_DiseaseOnCoffeeLeaves/sample/image_leaves.jpg'

    # Gọi hàm detect
    result_image = detect_leaf_disease(image_path)

    # Hiển thị kết quả
    # cv2_imshow(result_image)

    # Lưu kết quả
    cv2.imwrite('./detect_DiseaseOnCoffeeLeaves/detected_leaf.jpg', result_image)