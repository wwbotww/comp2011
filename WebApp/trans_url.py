import pandas as pd

# Read the input CSV file
input_file = 'anime_cleaned.csv'
output_file = 'anime.csv'

# Function to replace old domain with the new domain
def update_image_url(url):
    if isinstance(url, str) and 'myanimelist.cdn-dena.com' in url:
        return url.replace('myanimelist.cdn-dena.com', 'cdn.myanimelist.net')
    return url

# Load the dataset
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"File {input_file} not found, please check the path!")
    exit()

# Ensure the 'image_url' column exists
if 'image_url' not in df.columns:
    print("Column 'image_url' not found in the dataset, please check the input file!")
    exit()

# Replace links in the 'image_url' column
df['image_url'] = df['image_url'].apply(update_image_url)

# Save as a new CSV file
df.to_csv(output_file, index=False)
print(f"File has been saved to {output_file}")