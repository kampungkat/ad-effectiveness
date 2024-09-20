from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import os
import subprocess
import shutil
import pandas as pd

# Kaggle notebook and dataset constants
kernel_id='kampungkat/ad-detection'
dataset_id='kampungkat/ad-detect-test-images'
base_dir = '../kaggle_code/runs/detect'

# Function to format current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# Helper function to capture screenshots
def capture_screenshot(url):
    # Create a screenshots directory if it doesn't exist
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    # chrome_options.add_argument("--headless")  # Runs without a window i.e. headless mode

    # Set window sizes for both desktop (1920x1080) and mobile (360x800)
    devices = {
        "desktop": {"window_size": "--window-size=1920x1080"},
        "mobile": {
            "window_size": "--window-size=360x800",
            "mobile_emulation": {
                "deviceMetrics": {"width": 360, "height": 800, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36"
            }
        }
    }

    screenshot_paths = {}

    for device_type, config in devices.items():
        # Configure Chrome options based on device type
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument(config["window_size"])

        if device_type == "mobile":
            chrome_options.add_experimental_option("mobileEmulation", config["mobile_emulation"])

        # Initialize the WebDriver with the options
        driver = webdriver.Chrome(options=chrome_options)

        # Set a page load timeout of 30 seconds
        driver.set_page_load_timeout(30)

        try:
            # Attempt to load the page
            driver.get(url)
            time.sleep(15)  # Wait for the page to load
        except TimeoutException:
            print(f"Page load timeout for {url} on {device_type}. Skipping.")
            driver.quit()
            screenshot_paths[device_type] = None  # Set None in case of failure
            continue

        # Format the site name and timestamp
        site_name = url.replace('https://', '').replace('/', '_')
        timestamp = get_timestamp()

        # Capture full-page screenshot
        screenshot_path = f"screenshots/{site_name}_{device_type}_{timestamp}_full.png"
        driver.save_screenshot(screenshot_path)
        
        # Save the screenshot path
        screenshot_paths[device_type] = screenshot_path
        
        # Close the browser
        driver.quit()

    return screenshot_paths


def ad_effectiveness_score(ad_count, page_area, total_ad_area, ad_count_threshold=2, ad_area_threshold=0.3):
    # Calculate ad count score
    ad_count_score = min(1, ad_count_threshold / ad_count) if ad_count > 0 else 1
    # Calculate ad area score
    ad_area_score = min(1, (ad_area_threshold * page_area) / total_ad_area) if total_ad_area > 0 else 1
    # Final effectiveness score is the product of these two
    return ad_count_score, ad_area_score, ad_count_score * ad_area_score

def get_page_area(image_file):
    if 'mobile' in image_file:
        return 1080 * 2400  # Retina mobile resolution
    else:
        return 1654 * 2400  # Retina desktop resolution



# Helper function to collect the images and labels

def process_images_for_ad_effectiveness(base_dir, label_dir='predict/labels', image_dir='predict', class_mapping={0: 'ad_rectangle', 1: 'ad_square', 2: 'ad_vertical'}):
    # Define the full path to the labels and images
    label_path = os.path.join(base_dir, label_dir)
    image_path = os.path.join(base_dir, image_dir)
    
    # List to hold the data
    data = []

    # Iterate through each label file
    for label_file in os.listdir(label_path):
        if label_file.endswith('.txt'):  # Only process .txt files
            image_file = label_file.replace('.txt', '.png') 
            image_full_path = os.path.join(image_path, image_file)  # Full image path
            with open(os.path.join(label_path, label_file), 'r') as f:
                for line in f:
                    # YOLO format: class_id x_center y_center width height
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    ad_type = class_mapping[int(class_id)]
                    # Append to data list
                    data.append([image_full_path, ad_type, x_center, y_center, width, height])

    # Create a DataFrame from the collected data
    cols = ['image_file', 'ad_type', 'x_center', 'y_center', 'width', 'height']
    labels_df = pd.DataFrame(data, columns=cols)

    # Calculate ad area for each ad instance
    labels_df['ad_area'] = labels_df['width'] * labels_df['height'] * labels_df.apply(lambda row: get_page_area(row['image_file']), axis=1)

    # Group by image_file and calculate total_ad_area and ad_count
    ad_summary_df = labels_df.groupby('image_file').agg(
        total_ad_area=('ad_area', 'sum'),
        ad_count=('ad_area', 'size')
    ).reset_index()

    # Calculate page area for each image
    ad_summary_df['page_area'] = ad_summary_df['image_file'].apply(get_page_area)

    # Apply the ad effectiveness score function to each row
    ad_summary_df[['ad_count_score', 'ad_area_score', 'ad_effectiveness']] = ad_summary_df.apply(
        lambda row: ad_effectiveness_score(row['ad_count'], row['page_area'], row['total_ad_area']),
        axis=1,
        result_type='expand'
    )

    return ad_summary_df


# ad_summary_df = process_images_for_ad_effectiveness(base_dir)

# Display the resulting DataFrame with ad effectiveness scores
# print(ad_summary_df.head())

# Helper to upload screenshots into Kaggle

def check_dataset_version_status(dataset_id):
    print(f"Checking the status of the dataset: {dataset_id}")
    
    while True:
        # Run kaggle API command to check the dataset version
        kaggle_status_command = f'kaggle datasets status {dataset_id}'
        
        # Execute the command and capture the output
        result = subprocess.run(kaggle_status_command, shell=True, capture_output=True, text=True)
        
        # Check if the output contains the word 'complete'
        output = result.stdout
        
        if 'ready' in output:
            print(f"Dataset {dataset_id} versioning complete.")
            break
        elif 'error' in output:
            print(f"Dataset {dataset_id} versioning failed.")
            break
        else:
            print(f"Dataset {dataset_id} is still processing... Checking again in 30 seconds.")
            time.sleep(30)  # Wait 30 seconds before checking again

# Helper function to start the upload and waiting for completion
def upload_to_kaggle_version(folder_path, dataset_id='kampungkat/ad-detect-test-images', version_notes='Updated dataset'):
    # Compress the screenshots folder into a zip file
    shutil.make_archive('screenshots', 'zip', folder_path)
    
    # Use Kaggle API to upload a new version to the existing dataset
    kaggle_command = f'kaggle datasets version -p {folder_path} -m "{version_notes}"'
    
    # Execute the command
    result = subprocess.run(kaggle_command, shell=True)
    if result.returncode == 0:
        print(f"New version of dataset {dataset_id} uploaded successfully!")
        # Check if dataset versioning is complete
        check_dataset_version_status(dataset_id)
    else:
        print(f"Failed to upload new version of dataset {dataset_id}!")


# Helper to run Kaggle notebook

def trigger_kaggle_kernel():
    # Trigger the kernel using Kaggle API
    kaggle_command = f'kaggle kernels push -p ../kaggle_code/'
    
    # Execute the command
    result = subprocess.run(kaggle_command, shell=True)
    
    if result.returncode == 0:
        print(f"Kernel triggered successfully!")
    else:
        print(f"Failed to trigger kernel!")

# Helper function to check kernel (notebook) status
def check_kernel_status(kernel_id):
    # Check the kernel status using Kaggle API
    kaggle_command = f'kaggle kernels status {kernel_id}'
    
    # Execute the command to check status
    result = subprocess.run(kaggle_command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout.lower()
        
        if "complete" in output:
            print(f"Kernel {kernel_id} has completed.")
            return True
        elif "running" in output:
            print(f"Kernel {kernel_id} is still running.")
            return False
        else:
            print(f"Kernel {kernel_id} is in an unexpected state: {output}")
            return False
    else:
        print(f"Failed to check status for kernel {kernel_id}: {result.stderr}")
        return False

def wait_for_kernel_completion(kernel_id, check_interval=10):
    print(f"Waiting for kernel {kernel_id} to complete...")
    
    # Loop until the kernel is completed
    while True:
        if check_kernel_status(kernel_id):
            break  # Kernel has completed, break the loop
        else:
            print(f"Kernel {kernel_id} still running. Checking again in {check_interval} seconds.")
            time.sleep(check_interval)  # Wait for the specified interval before checking again

def download_predictions_from_kernel(kernel_id, destination_folder):
    # Wait for the kernel to complete
    wait_for_kernel_completion(kernel_id)
    
    # Download the kernel output
    kaggle_command = f'kaggle kernels output {kernel_id} -p {destination_folder}'
    
    # Execute the command to download the output files
    result = subprocess.run(kaggle_command, shell=True)
    
    if result.returncode == 0:
        print(f"Predictions downloaded to {destination_folder}")
    else:
        print(f"Failed to download predictions from {kernel_id}")


def process_ad_effectiveness(domain):
    # Step 1: Capture screenshots
    screenshot_paths = capture_screenshot(domain)
    
    # Step 2: Upload screenshots as a new dataset version
    upload_to_kaggle_version('screenshots')
    
    # Step 3: Trigger the Kaggle kernel to process predictions
    trigger_kaggle_kernel()
    
    # Step 4: Wait for the kernel to complete and download predictions
    wait_for_kernel_completion(kernel_id)
    download_predictions_from_kernel(kernel_id, '../kaggle_code/')

    # Step 5: Process the predictions to calculate ad effectiveness
    ad_summary_df = process_images_for_ad_effectiveness(base_dir)
    
    return ad_summary_df
