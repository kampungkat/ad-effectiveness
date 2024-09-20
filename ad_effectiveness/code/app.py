import streamlit as st
from PIL import Image
from helpers import process_ad_effectiveness

import streamlit as st
from PIL import Image
from helpers import process_ad_effectiveness

def run_app():
    st.title('Ad Effectiveness on Web Pages')

    domain = st.text_input('Enter domain or URL:')
    if st.button('Analyze'):
        if domain:
            # Process the domain and get ad effectiveness and image paths
            ad_summary_df = process_ad_effectiveness(domain)

            # Display the desktop version
            desktop_data = ad_summary_df[ad_summary_df['image_file'].str.contains('desktop')]
            if not desktop_data.empty:
                st.subheader(f'Desktop Version of {domain}')
                desktop_ad_score = desktop_data['ad_effectiveness'].values[0]
                desktop_img_path = desktop_data['image_file'].values[0]
                
                # Load and display image with ad boundaries
                desktop_img = Image.open(desktop_img_path)
                st.image(desktop_img, caption=f"Ads detected on the desktop version of {domain}")
                st.write(f"Desktop Ad Effectiveness Score: {desktop_ad_score}")
            else:
                st.error(f"No ads detected in the desktop version of {domain}.")

            # Display the mobile version
            mobile_data = ad_summary_df[ad_summary_df['image_file'].str.contains('mobile')]
            if not mobile_data.empty:
                st.subheader(f'Mobile Version of {domain}')
                mobile_ad_score = mobile_data['ad_effectiveness'].values[0]
                mobile_img_path = mobile_data['image_file'].values[0]
                
                # Load and display image with ad boundaries
                mobile_img = Image.open(mobile_img_path)
                st.image(mobile_img, caption=f"Ads detected on the mobile version of {domain}")
                st.write(f"Mobile Ad Effectiveness Score: {mobile_ad_score}")
            else:
                st.error(f"No ads detected in the mobile version of {domain}.")
        else:
            st.error('Please enter a valid URL.')


# Run the app
if __name__ == '__main__':
    run_app()