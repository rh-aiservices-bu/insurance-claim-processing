from ultralytics import YOLO

def predict(best_model_path, car_image_path):
    model = YOLO(best_model_path)
    results = model.predict(car_image_path)
    return results[0]