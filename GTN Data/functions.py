import pandas as pd
from bs4 import BeautifulSoup
import random
import requests
import time
import math
import csv
def scrape_amazon(search_url, max_pages=2, output_file="amazon.csv"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    results = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        paginated_url = f"{search_url}&page={page}"
        
        try:
            response = requests.get(paginated_url, headers=headers, timeout=10)
            response.raise_for_status()  
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", {"data-component-type": "s-search-result"})

        for product in products:
            try:
                
                name_tag = product.find("h2")
                name = name_tag.text.strip() if name_tag else "N/A"

                
                url_tag = product.find("a", class_="a-link-normal s-line-clamp-4 s-link-style a-text-normal")
                if url_tag:
                    url = url_tag["href"]
                else:
                    
                    alt_url_tag = product.find("a", class_="a-link-normal s-line-clamp-2 s-link-style a-text-normal")
                    url = alt_url_tag["href"] if alt_url_tag else None

                full_url = f"https://www.amazon.com{url}" if url and url.startswith("/") else "N/A"

                
                price_whole = product.find("span", class_="a-price-whole")
                price_fraction = product.find("span", class_="a-price-fraction")
                if price_whole and price_fraction:
                    price = f"{price_whole.text.strip()}.{price_fraction.text.strip()}"
                else:
                    price = "N/A"

                
                list_price_tag = product.find("span", class_="a-price a-text-price")
                if list_price_tag:
                    non_discounted_price_tag = list_price_tag.find("span", class_="a-offscreen")
                    try:
                        non_discounted_price = (
                            float(non_discounted_price_tag.text.replace("$", "").strip())
                            if non_discounted_price_tag
                            else math.nan
                        )
                    except ValueError:
                        non_discounted_price = math.nan
                else:
                    non_discounted_price = math.nan

                
                results.append({
                    "Item Name": name,
                    "Item URL": full_url,
                    "Price": price,
                    "Non-Discounted Price": non_discounted_price if not math.isnan(non_discounted_price) else "N/A"
                })
            except AttributeError:
                
                continue
        
        # Pause with randomness to avoid detection
        time.sleep(random.uniform(2, 5))

    # Save results to CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Item Name", "Item URL", "Price", "Non-Discounted Price"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Scraping complete. Data saved to {output_file}.")

def scrape_amazon_asins(asins, output_file="amazon_asin_data.csv"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    results = []

    for asin in asins:
        product_url = f"https://www.amazon.com/dp/{asin}"
        print(f"Scraping ASIN: {asin}")

        try:
            response = requests.get(product_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ASIN {asin}: {e}")
            results.append({
                "ASIN": asin,
                "Error": f"Failed to fetch page: {e}"
            })
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            # Item Name
            name_tag = soup.find("span", id="productTitle")
            item_name = name_tag.text.strip() if name_tag else "N/A"

            # Price
            price_tag = soup.find("span", class_="a-price")
            if price_tag:
                price_whole = price_tag.find("span", class_="a-price-whole")
                price_fraction = price_tag.find("span", class_="a-price-fraction")
                if price_whole and price_fraction:
                    price = f"${price_whole.text.strip()}.{price_fraction.text.strip()}"
                else:
                    price = "N/A"
            else:
                price = "N/A"

            # Buy Box Seller
            buy_box_seller = "N/A"
            offer_container = soup.find('div', class_='offer-display-features-container')
            if offer_container:
                seller_element = offer_container.find(
                    'span', class_='offer-display-feature-text-message'
                )
                buy_box_seller = seller_element.get_text(strip=True) if seller_element else "N/A"

            # Ratings
            ratings_tag = soup.find("i", class_="a-icon-star")
            ratings = ratings_tag.text.strip() if ratings_tag else "N/A"

            # Ratings Count
            ratings_count_tag = soup.find("span", id="acrCustomerReviewText")
            ratings_count = ratings_count_tag.text.strip() if ratings_count_tag else "N/A"

            # Fix for "Make Sure This Fits"
            make_sure_fits = False
            fitment_card = soup.find("div", id="automotive-pf-primary-view-default")
            if fitment_card:
                fits_element = fitment_card.find("span", id="automotive-pf-primary-view-default-make-sure-this-fits")
                make_sure_fits = fits_element is not None

            # Total Offers
            offers_box = soup.find("div", id="dynamic-aod-ingress-box")
            total_offers = offers_box.get_text(strip=True) if offers_box else "N/A"

            # Extract Main Image Only
            main_image_url = "N/A"
            image_div = soup.find("div", id="imgTagWrapperId")
            if image_div:
                main_image = image_div.find("img")
                main_image_url = main_image["src"] if main_image and main_image.get("src") else "N/A"

            # Extract "OEM Part Number" and "Manufacturer Part Number"
            oem_part_number = "N/A"
            manufacturer_part_number = "N/A"
            product_details_table = soup.find("table", id="productDetails_techSpec_section_1")
            if product_details_table:
                rows = product_details_table.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    value = row.find("td")
                    if header and value:
                        header_text = header.get_text(strip=True)
                        value_text = value.get_text(strip=True)
                        if header_text == "OEM Part Number":
                            oem_part_number = value_text
                        elif header_text == "Manufacturer Part Number":
                            manufacturer_part_number = value_text

            # Extract Full Browse Node Category
            browse_node_category = "N/A"
            breadcrumbs = soup.find("ul", class_="a-unordered-list a-horizontal a-size-small")
            if breadcrumbs:
                categories = breadcrumbs.find_all("a", class_="a-link-normal a-color-tertiary")
                browse_node_category = ", ".join([cat.text.strip() for cat in categories])

            # Shipping Information
            shipping_tag = soup.find("div", id="mir-layout-DELIVERY_BLOCK")
            shipping_info = shipping_tag.text.strip() if shipping_tag else "N/A"

            results.append({
                "Item Name": item_name,
                "Price": price,
                "Buy Box Seller": buy_box_seller,
                "Ratings": ratings,
                "Ratings Count": ratings_count,
                "Make Sure Fits": make_sure_fits,
                "Total Offers": total_offers,
                "Main Image URL": main_image_url,
                "OEM Part Number": oem_part_number,
                "Manufacturer Part Number": manufacturer_part_number,
                "Full Browse Node Category": browse_node_category,
                "ASIN": asin,
                "Shipping": shipping_info
            })
        except Exception as e:
            print(f"Error parsing ASIN {asin}: {e}")
            results.append({
                "ASIN": asin,
                "Error": f"Failed to parse page: {e}"
            })

        time.sleep(random.uniform(2, 5))

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "Item Name", "Price", "Buy Box Seller", "Ratings", "Ratings Count",
            "Make Sure Fits", "Total Offers", "Main Image URL", "OEM Part Number",
            "Manufacturer Part Number", "Full Browse Node Category", "ASIN", "Shipping"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Scraping complete. Data saved to {output_file}.")
