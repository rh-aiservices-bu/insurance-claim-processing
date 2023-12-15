# car-accident-detection
car accident detection model

Simple, unstructured and unopinionated project for data science.  The purpose is to allow data science exploration to easily transition into deployed services and applications on the Red Hat OpenShift AI platform.

We are working with the YOLO8 object detection model.

## Project Organization
```
├── README.md
├── requirements.txt                          <- Used to install packages for model training and notebook usage
├── 1-explore-data.ipynb                      <- Notebook to explore un-trained YOLO8 model
├── 2-detect-car-with-boxes.ipynb             <- Notebook to show how to use a YOLO8 model and detect a car and place labels and associated probability of the image being a car onto the car image
├── 3-retrain-model-for-accident-detection.ipynb    <- Notebook used to retrain YOLO8 model with roboflow (Guillaume's) accident detection dataset
├── 4-test-retrained-model.ipynb              <- Notebook used to test the retrained YOLO8 model (saved as best.pt in /models)
├── 5-predict.ipynb                           <- Notebook used to call the predict() in Prediction.py
├── .gitignore                                <- standard python gitignore
├── Prediction.py                             <- Python file containing the predict() function based on functions in Prediction2.ipynb
├── Prediction.ipynb                          <- Notebook for testing prediction and drawing boxes/label with Chris's draw_boxes and draw_bounding_box_pn image functions
├── Prediction2.ipynb                         <- Notebook for testing prediction and drawing boxes/label with default 'Immage.fromarray' function
└── data.yaml                                 <- YAML file used to point to Roboflow image set with 'moderate' and 'severe' labelled images.
--------

First 2 notebooks (1&2) initially trained with a yolo model trained on a small 500 image dataset I created.  Once Guillaume's dataset was chosen, I downloaded it and set up a RHOAI workbench with
sufficient RAM/GPU/Storage.  The remainder of the notebook development was performed on the yolo model 'best.pt' which was copied into the /models folder.  Refer to notebook 3-retrain-model-for-accident-detection
to view number of epochs used, box_loss, cls_loss and Mean Average Precision (MAP50-95).

Images used for testing with above notebooks can be found in /images folder.  There are 4 images.  CarImage1 & 3 contain image of a single vehicle accident.  CarImage1 contains the image of a multi
car accident.  CarImage0 contains the image of a vehicle not involved in an accident and is used specifically for notebooks 1 &2.

Notebooks were created and run on RHOAI notebook image server 'OpenVINO Toolkit' which uses Python v3.8.  YOLO8 does not work in our newer notebook images which contain Python versions 3.9 and
above.  Therefore the Standard Data Science notebook images did not work. Standard Data Science notebook image Version 1.2 which contains Python v3.8 and Version 2023.1 which contains Python v3.9, neither of which
could handle running a YOLO8 model.
