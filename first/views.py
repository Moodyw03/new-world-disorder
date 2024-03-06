from django.http import Http404
import requests
from django.shortcuts import render
import json
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

def fetch_product_data(api_url, headers):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def list_printful_products(request):
    api_key = 'P1pHaofDN94gYPU1mxGaxP2PBHLOyjam63yY1EYP'
    first_api_url = 'https://api.printful.com/store/products'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Fetch product IDs from the first API endpoint
    data = fetch_product_data(first_api_url, headers)
    
    if data and data.get('result'):
        products = data['result']  # Retrieve all products from the API response
        detailed_product_data = []
        
        for product in products:
            product_id = product['id']
            second_api_url = f'https://api.printful.com/store/products/{product_id}'
            detailed_product_data.append(fetch_product_data(second_api_url, headers))
        
        # Call managejsonify() function and get the JSON data
        json_data = managejsonify(detailed_product_data)
        
        # Pass the JSON data to the template context
        context = {
            'products': json_data,
        }
        
        # Render the template with the product data in the context
        return render(request, 't.html', context)

# this function is managing my api response in order get the desire data from the api
def managejsonify(product_data):
    simplified_products = []

    for product in product_data:
        if 'result' in product and 'sync_product' in product['result']:
            product_info = product['result']['sync_product']
            variants = product['result'].get('sync_variants', [])

            simplified_product = {
                'id': product_info['id'],
                'name': product_info['name'],
                'thumbnail_url': product_info.get('thumbnail_url', 'No Thumbnail Available'),
                'variants': []
            }

            for variant in variants:
                variant_info = {
                    'variant_id': variant['id'],
                    'name': variant['name'],
                    'size': variant.get('size', 'Unknown Size'),
                    'color': variant.get('color', 'Unknown Color'),
                    'price': variant.get('retail_price', 'No Price Available'),
                    'currency': variant.get('currency', 'No Currency Available'),
                    'image_url': variant['product']['image'] if 'product' in variant and 'image' in variant['product'] else 'No Image Available'
                }
                simplified_product['variants'].append(variant_info)

            simplified_products.append(simplified_product)

    return simplified_products
def Home(request):
    return render(request, "a.html")





def product_detail(request, productId):
    api_key = 'P1pHaofDN94gYPU1mxGaxP2PBHLOyjam63yY1EYP'
    api_url = f'https://api.printful.com/store/products/{productId}'
    headers = {'Authorization': f'Bearer {api_key}'}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        product_info = data['result']['sync_product']
        variants_info = data['result']['sync_variants']
        product = {
            'id': product_info['id'],
            'name': product_info['name'],
            'thumbnail_url': product_info['thumbnail_url'],
            'variants': variants_info
        }
    except requests.RequestException:
        raise Http404("Product does not exist")

    return render(request, 'product_detail.html', {'product': product})

import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        # Extracting recipient and item details from the request body
        body_unicode = request.body.decode('utf-8')
        order_data = json.loads(body_unicode)

        # Prepare the API request payload
        payload = {
            "recipient": order_data['recipient'],
            "items": order_data['items']
        }

        # Set up the API endpoint and headers
        api_url = 'https://api.printful.com/orders'
        headers = {
            'Authorization': 'Bearer PlRLr2kzXugl1YMRF9k97SGTh9ztgh2e5TYcmlPy',
            'Content-Type': 'application/json'
        }

        # Make the POST request to Printful API
        response = requests.post(api_url, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return HttpResponse(response.text, status=response.status_code)
    else:
        return HttpResponse('Method not allowed', status=405)
