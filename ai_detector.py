from PIL import Image

def detect_problem(image_path):
    """
    Prototype detector.
    This validates the image and returns a demo result.
    Replace this function with a trained computer-vision model
    (for example YOLO/PyTorch) when the model is available.
    """
    try:
        image=Image.open(image_path)
        width,height=image.size
        if width<100 or height<100:
            return {"problem_type":"Unknown","severity":"LOW","confidence":50}
    except Exception:
        return {"problem_type":"Unknown","severity":"LOW","confidence":0}

    return {"problem_type":"Pothole","severity":"HIGH","confidence":94}