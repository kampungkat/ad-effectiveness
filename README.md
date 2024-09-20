
# **Ad Impact Decoded: Using AI to measure Ad Effectiveness**

---

## **Overview**
Digital advertising started 30 years ago, with a simple banner on (hot)wired.com - and has evolved with new and innovative ad formats such as video, audio and nowadays even in AR / VR.

However, there have been real problems across the industry over the past decade around too many advertisements flooding users screens and devices.

For end users, there are remediations available through browser plugins which can block out annoying and intrusive ads.

However, for advertisers, there are no pre-emptive safeguards or tools which can block their brands from being displayed on cluttered ad environments



## **Problem Statement**
This project is a proof-of-concept to determine how ad effectiveness can be used to score and rank pages and sites, to prevent any spends on sites with ad clutter.


## **Objectives**: 
1. To apply computer vision and AI to identify ads on webpages on multiple sites and platforms
2. Propose an Ad Effectiveness metric to score ads detected above
3. Create a live app which can detect and then score ads based on Ad Effectiveness

---
### **Dataset**

- Screenshots of websites captured using Selenium
- Ads labeled and annotated using labeling tools (labelImg)

### **Models and tools**

- Selenium (for data collection)
- labelImg (for annotating)
- YOLOv5 / v8 (CV Model)
- PyTorch
- Kaggle (for hosting and running models)
- Streamlit (for live demo)


### **Final Deliverables**

- **Live Demo**: A working demonstration of the ad detection and effectiveness scoring system. Located in `/code/app.py`
- **Final Notebooks and Assets**: 
    - Notebooks located in `/notebooks/`
    - Final dataset with images and labels located in `\dataset\` 
    - Model and kaggle related code in `\kaggle_code\`


- **Presentation Slides**: [Link](https://docs.google.com/presentation/d/1W1FpnUE_kUOONOb2FAQgKmO3M_N64gbL41WJLtpZSIY/edit?usp=sharing)

## **Project Summary**
The following steps were performed in order:

1. **Raw data Collection (code in `\notebooks\notebook1`)**

    We used Selenium to scrape and take screenshots from a list of 350-odd sites in both desktop and mobile formats.

2. **Image annotation using [LabelImg](https://github.com/HumanSignal/labelImg)**
    
    The class count was kept simple and easy to remember:
    0: ad_rectangle, 1: ad_square, 2: ad_vertical

3. **Train-val split (code in \notebooks\notebook2)**
    
    The images and annotated were then split into train-validations sets at an 80/20 ratio.

4. **Ad Effectiveness Score evaluation (code in \notebooks\notebook3)**
    
    Ad effectiveness score is considered as a combination of ad count (ratio) and the ad density (ad area) on a page. 
    Ad effectiveness = ad count ratio x ad density
    For a clear explanation, please refer to the [presentation linked here](https://docs.google.com/presentation/d/1W1FpnUE_kUOONOb2FAQgKmO3M_N64gbL41WJLtpZSIY/edit?usp=sharing)

5. **Model training**
    
    Both models (YOLOv5 and YOLOv8) were trained on Kaggle - transfer learning with default layers and model parameters left in place.
    |Model| Runs|mAP-50 score| Best model run|Time taken|Link to notebook|GPU|
    |-|-|-|-|-|-|-|
    |YOLOv5|50|90.0|49|1 hr 57 mins|[link](https://www.kaggle.com/code/kampungkat/yolov5-gpu)|Tesla P100-PCIE-16GB|
    |**YOLOv8**|**50**|**93.4**|**48**|**42 mins**|**[link](https://www.kaggle.com/code/kampungkat/yolov8-gpu)**|**Tesla P100-PCIE-16GB**|
    |YOLOv8|50|93.4|48|9 hrs 18 mins|[link](https://www.kaggle.com/code/kampungkat/yolov8-cpu-9h/notebook)|no|

    The YOLOv8 model proved to be the best in terms of speed and score (mAP-50). The GPU was used sparingly (~46 minutes) for each run.

6. **Model inference / Detection**

    The best model (saved as `/kaggle_code/best.pt`) was used to detect ads from new unseen images.

    This code is running on Kaggle on [this link](https://www.kaggle.com/code/kampungkat/ad-detection)

7. **Streamlit App (code in /code/app.py)**

    We also wrote a simple Streamlit app for a live demo - for now, this runs locally. The app also uses makes extensive use of helper functions (code in /code/helpers.py)to upload image data into Kaggle, run the detection notebook, download the output, calculate the Ad effectiveness score and finally display the annotated images with their ad effectiveness score.

## **Conclusion**

Ad clutter is an critical obstacle for advertisers and marketers trying to get the most of their ad spend budgets.
Using ad effectiveness scores as a governing criteria, and super-charging it with computer vision AI tools, ad campaigns and budgets can be deployed more judiciously and with care.
