# car-accident-detection
car accident detection model

Simple, unstructured and unopinionated project for data science.  The purpose is to allow data science exploration to easily transition into deployed services and applications on the Red Hat OpenShift AI platform.

We are working with the YOLO8 object detection model.

## Project Organization

```text
├── README.md
├── requirements.txt             <- Used to install packages for model training and notebook usage
├── 04-01-over-approach.ipynb    <- Notebook to explore un-trained YOLO8 model
├── 04-02-car-recognition.ipynb  <- Notebook to show how detect the car and place information and bounding boxes on the image
├── 04-03-model-retraining.ipynb <- Notebook used to retrain YOLO8 model with Roboflow accident detection dataset
├── 04-04-accident-recog.ipynb   <- Notebook used to test the retrained YOLO8 model
├── 04-05-serving-manual.ipynb   <- Notebook used to query the model served from RHOAI
--------
```
