from django.http import Http404
import requests
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required



# Function for the fetching the Product
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
    return render(request, "cart.html")





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

@csrf_exempt

@require_POST


def place_order(request):
    print("Request received")
    api_url = 'https://api.printful.com/orders'
    api_key = 'PlRLr2kzXugl1YMRF9k97SGTh9ztgh2e5TYcmlPy'
    # Parse JSON data from the request body
    data = json.loads(request.body)
    items = data.get('items', [])  # Get the list of items, default to an empty list if not found
    for product in items:
              variant_id = product.get('variant_id')
              quantity = product.get('quantity')
              image_url = product.get('image_url')
             
              
    # Now, variant_id, quantity, and image_url refer to the current product in the loop
    # Recipient details coming from the AJAX request
    recipient_details = data.get('recipient', {})
    # Forming the order details
    order_data = {
        "recipient": {
            "name": recipient_details.get('name', ''),
            "address1": recipient_details.get('address1', ''),
            "country": recipient_details.get('country', ''),
            "city": recipient_details.get('city', ''),
            "state": recipient_details.get('state', ''),
            "state_code": recipient_details.get('state_code', ''),
            "country_code": recipient_details.get('country_code', ''),
            "zip": recipient_details.get('zip', '')
        },
        "items": [
            {
                "variant_id": variant_id,
                "quantity": 1,
                "files": [
                    {
                        "type": "default",
                        "url": image_url
                    }
                ]
            }
        ]
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(api_url, json=order_data, headers=headers)
    print(response.status_code)

    if response.status_code == 200 or response.status_code == 201:
       
        

        return JsonResponse({'status': 'success', 'message': 'Order placed successfully.'})
    else:
        # Handle error
        response_data = response.json()
        error_message = response_data.get('error', {}).get('message', 'Unknown error occurred.')
        return JsonResponse({'status': 'error', 'message': error_message}, status=400)



def proxy_to_external_api(request):
    # Make a GET request to the external API
    response = requests.get('https://api.printful.com/countries')
    
    # Return the API response as a JSON response
    return JsonResponse(response.json(), safe=False)  

# external_api_url = f'https://api.printful.com/states/{country_code}'

def get_states_for_country(request, country_code):
    try:
        external_api_url = f'https://api.printful.com/states/{country_code}'
        response = requests.get(external_api_url)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            # Log unexpected status codes
            print(f"Error fetching states: {response.status_code}")
            return JsonResponse({'error': 'Failed to fetch states from external API'}, status=500)
    except Exception as e:
        # Log any exceptions thrown during processing
        print(f"Exception occurred: {e}")
        return JsonResponse({'error': 'An error occurred processing your request'}, status=500)
    




