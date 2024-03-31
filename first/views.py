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
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Function for the fetching the Product
def fetch_product_data(api_url, headers):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

from django.http import HttpResponse
from django.shortcuts import render

def list_printful_products(request):
    api_key = 'PlRLr2kzXugl1YMRF9k97SGTh9ztgh2e5TYcmlPy'
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
        
    else:
        # Handle the case where data or 'result' key is missing
        return HttpResponse("Error: No product data found")









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


def Home1(request):
    return render(request, "check.html")


def product_detail(request, productId):
    api_key = 'PlRLr2kzXugl1YMRF9k97SGTh9ztgh2e5TYcmlPy'
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




@csrf_exempt
def place_order(request):
    print("Request received")
    if request.method == "POST":
        try:
            api_url = 'https://api.printful.com/orders'
            api_key = 'PlRLr2kzXugl1YMRF9k97SGTh9ztgh2e5TYcmlPy'
            
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Extract recipient details from the request
            recipient_details = data.get('recipient', {})
            
            # Initialize the items list for the API request
            items_for_api = []
            
            # Iterate over each item in the received items list
            for item in data.get('items', []):
                # Extract item details
                variant_id = item.get('variant_id')
                quantity = item.get('quantity')
                price = item.get('price')
                
                image_url = item.get('image_url')  # Correctly structured from the client
                
                # Append item details, including the image_url inside 'files'
                items_for_api.append({
                    "variant_id": variant_id,
                    "quantity": quantity,
                    "price":price,
                    "files": [
                        {
                            "type": "default",
                            "url": image_url
                        }
                    ]
                })
             
            
            # Forming the complete order data for the API request
            order_data = {
                "recipient": recipient_details,
                "items": items_for_api
            }
            print(order_data)
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Sending the order to the external API
            response = requests.post(api_url, json=order_data, headers=headers)
            # print(response.status_code)
            
            if response.status_code in [200, 201]:
                # Retrieve the current order history from the session or initialize it if not present
                order_history = request.session.get('order_history', [])
                
                # Append the new order to the order history list
                order_history.append(order_data)
                
                # Save the updated order history back to the session
                request.session['order_history'] = order_history
                request.session.modified = True  # Mark the session as modified to save changes
                
                return JsonResponse({'status': 'success', 'message': 'Order placed successfully.'})
            else:
                # Handle API error
                error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
                return JsonResponse({'status': 'error', 'message': error_message}, status=400)
        except Exception as e:
    # If there's an error, return an error response with the error message
            error_message = str(e)
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'This endpoint expects a POST request.'}, status=405)








def view_order_history(request):
    order_history = request.session.get('order_history', [])

    # Optional: Debugging print to verify the structure of order_history
    for order in order_history:
        for item in order.get("items", []):
            if item.get("files"):
                print("Verified Image URL:", item["files"][0].get("url", "No Image URL"))

    return render(request, 'order_history.html', {'order_history': order_history})




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
    


stripe.api_key = 'sk_test_51OvFQwRxR89gpN14N8XjbY56QV35xqruH9YCS5yxCWeubXlIY9DWAgxTX5BxKTDGqwTOj5C9n1gp3Q0CMDIdAWFv00kYUL9lOd'

import json
from django.http import JsonResponse

def create_payment(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            

            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=00,  # Replace with your calculation logic
                currency='gbp',
                payment_method_types=['card'],
                # Optionally, you can add metadata or other parameters here
            )

            # Serialize the response data to JSON
            response_data = {
                'clientSecret': intent.client_secret
            }

            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        

def payment_form(request):
    return render(request, 'payment_form.html')        