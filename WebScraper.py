import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def extract_contents(url):
    """
    Extracts the item category from a given URL.

    Args:
        base_url (str): The base URL to scrape.

    Returns:
        BeautifulSoup: The parsed HTML content.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def transform_item_category(soup):
    """
    Transforms the item category in the given soup object.

    Args:
        soup (BeautifulSoup): The soup object containing the HTML.

    Returns:
        list: The list of transformed item categories.
    """
    # Find all the divs with the specified class
    divs = soup.find_all('div', class_='MegaMenuHiddenCategoryListWrapper--11chaob eFolqZ')

    # Iterate over each div
    for item in divs:
        # Find all the anchor tags with the specified class
        url_item_category = item.find_all('a', class_='CategoryHiddenLink--1qv7ebj dYGUuu')

        # Iterate over each anchor tag
        for item in url_item_category:
            # Get the href attribute value
            category = item['href']

            # Append the base URL to the category
            category = base_url + category

            # Append the transformed category to the list
            item_url_category_list.append(category)

    # Return the transformed item categories
    return item_url_category_list


def transform_items(soup):
    """
    Transform the items in the soup object.

    Args:
        soup: BeautifulSoup object containing the HTML data.

    Returns:
        List of transformed item URLs.
    """
    # Find all div elements with class 'ColListing--1fk1zey iowyBD'
    divs = soup.find_all('div', class_='ColListing--1fk1zey iowyBD')

    # Iterate over each div element
    for item in divs:
        # Find all anchor elements with class 'ProductCardHiddenLink--v3c62m dGWlVm'
        url_item = item.find_all('a', class_='ProductCardHiddenLink--v3c62m dGWlVm')
        # Iterate over each anchor tag
        for item in url_item:
            # Get the href attribute value
            item_url = item['href']

            # Append the transformed item URL to the list
            item_url_list.append(item_url)

    return item_url_list

def transform_product_info(product_content):
    """
    Transform the product information extracted from the website.

    Args:
        product_content (BeautifulSoup): The content of the website page.

    Returns:
        None
    """
    try:
        # Find all div elements with class 'ColListing--1fk1zey iowyBD'
        divs = product_content.find_all('div', class_='ProductDetails--1sb8xji jrwVWG')

        for product_info in divs:
            picture = None

            try:
                # Find the div element with class 'PdpMainImage--kopilf flXmdr'
                ImageDiv = product_info.find_all('div', class_='PdpMainImage--kopilf flXmdr')

                for link in ImageDiv:
                    # Find the img element with a src attribute
                    ImageURL = link.find_all('img', src=True)
                    image_src = [x['src'] for x in ImageURL]

                    # url is definitely correct, fetch the image
                    response = requests.get(image_src[0])
                    picture = sqlite3.Binary(response.content)

                if picture is None:
                    # Find the div element with class 'PdpImage--7pr6pv dNwcTc'
                    ImageDiv = product_info.find_all('div', class_='PdpImage--7pr6pv dNwcTc')

                    for link in ImageDiv:
                        # Find the img element with a src attribute
                        ImageURL = link.find_all('img', src=True)
                        image_src = [x['src'] for x in ImageURL]

                        # url is definitely correct, fetch the image
                        response = requests.get(image_src[0])
                        picture = sqlite3.Binary(response.content)

            except:
                picture = None

            # Extract the product information
            ProductName = product_info.find('h2', class_='PdpInfoTitle--1qi97uk sZrqX').text.strip()
            ProductPrice = product_info.find('span', class_='PdpMainPrice--4c0ljm bBOazG').text.strip()
            ProductSKU = product_info.find('div', class_='ProductNumber--jhh79i iNtHsC').text.strip().replace('Product Number: ','')
            ProductDescription = product_info.find('span', class_='PdpDescriptionWrapper--7s9nb3 cEhkaI').text.strip()

            # Create a Product object and add it to the database
            db_Product = Product(None, ProductName, ProductSKU, ProductPrice, ProductDescription, picture, datetime.now())
            db.add_product(db_Product)
    except Exception as e:
        # Log the error
        logging.error(f"An error occurred: {str(e)}")
        # Close the log file handler
        logging.shutdown()
    return


class Product:
    def __init__(self, product_id, product_name, product_sku, product_price, product_description, picture, creation_date):
        """
        Initialize the Product object with the given parameters.

        Args:
            product_id (int): The ID of the product.
            product_name (str): The name of the product.
            product_sku (str): The SKU of the product.
            product_price (float): The price of the product.
            product_description (str): The description of the product.
            picture (str): The picture of the product.
            creation_date (str): The creation date of the product.
        """
        self.product_id = product_id
        self.product_name = product_name
        self.product_sku = product_sku
        self.product_price = product_price
        self.product_description = product_description
        self.picture = picture
        self.creation_date = creation_date

class ProductDatabase:
    def __init__(self, db_name):
        """
        Initialize the class and connect to the database.
        
        Args:
            db_name (str): The name of the database.
        """
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        """
        Create a table called 'Products' if it doesn't already exist in the database.
        The table has columns for product information such as id, name, SKU, price, description, image, and creation date.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_Name Varchar(100) UNIQUE,
                Product_SKU Varchar(100),
                Product_Price Varchar(100),
                Product_Description Varchar(100),
                Product_Image BLOB,
                Product_CreationDate timestamp
            )
        ''')
        self.conn.commit()
        cursor.close()

    def add_product(self, product):
        """
        Add a product to the database.

        Args:
            product (Product): The product to be added.

        Returns:
            None
        """
        cursor = self.conn.cursor()

        # Insert product data into the Products table
        cursor.execute('''
            INSERT INTO Products (product_Name, Product_SKU, Product_Price, Product_Description, Product_Image, Product_CreationDate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product.product_name, product.product_sku, product.product_price, product.product_description, product.picture, product.creation_date))

        self.conn.commit()
        cursor.close()


if __name__ == "__main__":
    print('Starting Item URL List extraction')
    db = ProductDatabase('product_db.sqlite')
    base_url = f'https://shop.supervalu.ie'
    # Initialize the list to store the transformed item categories
    item_url_category_list = []
    # List to store the transformed item URLs
    item_url_list = []
    # Configure the logging settings
    log_filename = 'error.log'

    logging.basicConfig(
        filename=log_filename,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    categoryList = extract_contents(base_url)
    transform_item_category(categoryList) 

    for category in item_url_category_list:
        content = extract_contents(category)
        transform_items(content)

    for product in item_url_list:
        content = extract_contents(product)
        transform_product_info(content)
  
