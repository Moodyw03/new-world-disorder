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
import aiohttp
import asyncio
from aiohttp import ClientSession
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.views.generic.base import TemplateView

# Initialize the items list for the API request
# Cookie expiration time (in seconds)
COOKIE_EXPIRATION = 3600  # 1 hour
# Function for the fetching the Product
def fetch_product_data(api_url, headers):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def list_printful_products(request):
    api_key = 'hasiNeN7xTMlLWqhGQjxj053nGdD4EA7ozfUi44B'
    first_api_url = 'https://api.printful.com/store/products'
    headers = {'Authorization': f'Bearer {api_key}'}

    # Fetch product IDs from the first API endpoint
    with requests.get(first_api_url, headers=headers, params={'limit': 40}) as response:
        data = response.json()  # Parse the JSON response

    if data and data.get('result'):
        products = data['result']  # Retrieve all products from the API response
        detailed_product_data = []

        for product in products:
            product_id = product['id']
            second_api_url = f'https://api.printful.com/store/products/{product_id}'
            with requests.get(second_api_url, headers=headers) as response:
                detailed_product_data.append(response.json())

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

    api_key = 'hasiNeN7xTMlLWqhGQjxj053nGdD4EA7ozfUi44B'
    api_url = f'https://api.printful.com/store/products/{productId}'
    headers = {'Authorization': f'Bearer {api_key}'}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        product_info = data['result']['sync_product']
        variants_info = data['result']['sync_variants']
        for var in variants_info:
             var['product']['image']=var["files"][2]["preview_url"]

        product = {
            'id': product_info['id'],
            'name': product_info['name'],
            'thumbnail_url': product_info['thumbnail_url'],
            'variants': variants_info

        }
        print("here")
        variant_ino = variants_info[0]
        print(variant_ino["files"][2]["preview_url"])

    except requests.RequestException:
        raise Http404("Product does not exist")

    return render(request, 'product_detail.html', {'product': product})

@csrf_exempt
def place__cart_order(request):
    print("Request received")
    print(request)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            save_cart_data(data,request)
            return JsonResponse({'status': 'success', 'message': 'cart data saved successfully.'})
        except Exception as e:
            error_message = str(e)
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'This endpoint expects a POST request.'}, status=405)

def save_cart_data(data,request):
        
     # Check if there is a pending order in the session
        if 'cart_order' in request.session:
            del request.session['cart_order']  # Delete the existing pending order
        
        # Convert order data to JSON string
        order_data_json = json.dumps(data)
   
        # Store order data in session
        request.session['cart_order'] = order_data_json
       
        print("done")
        order_cart_json = request.session.get('cart_order')
        print(order_cart_json)
        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Order data saved successfully'})


@require_POST
@csrf_exempt
def place_order(request):
    print("Request received")
    print(request)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            recipient_details = data.get('recipient', {})
            items_for_api = []
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
                    "price": price,
                    "files": [{"type": "default", "url": image_url}]
                })
            order_data = {"recipient": recipient_details, "items": items_for_api}
            print("printing from order data")
            print(order_data)
            save_order_data(order_data, request)
            return JsonResponse({'status': 'success', 'message': 'Order data saved successfully.'})
        except Exception as e:
            error_message = str(e)
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'This endpoint expects a POST request.'}, status=405)

def save_order_data(data, request):
    try:
        # Check if there is a pending order in the session
        if 'pending_order' in request.session:
            del request.session['pending_order']  # Delete the existing pending order
        
        # Convert order data to JSON string
        order_data_json = json.dumps(data)
        print(order_data_json)
        # Store order data in session
        request.session['pending_order'] = order_data_json
       
        print("done")
        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Order data saved successfully'})
        
    except Exception as e:
        error_message = str(e)
        return JsonResponse({'status': 'error', 'message': error_message}, status=400)


@csrf_exempt
def send_order_to_printful(request):
    
    try:
        api_url = 'https://api.printful.com/orders'
        api_key = 'hasiNeN7xTMlLWqhGQjxj053nGdD4EA7ozfUi44B'
        order_data=request.session.get('pending_order')
        order_data=json.loads(order_data)
        print(order_data)
        del request.session['pending_order']
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        print(headers)
        print(order_data)
        # Sending the order to the external API
        response = requests.post(api_url, json=order_data, headers=headers)

        if response.status_code in [200, 201]:
         
            return {'status': 'success', 'message': 'Order placed successfully.'}
        else:
            # Handle API error
            error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
           
            return {'status': 'error', 'message': error_message}
    except Exception as e:
        # If there's an error, return an error response with the error message
        error_message = str(e)
        return {'status': 'error', 'message': error_message}
@csrf_exempt
def send_order_to_printful_cart(order_data,request) :

    try:
        api_url = 'https://api.printful.com/orders'
        api_key = 'hasiNeN7xTMlLWqhGQjxj053nGdD4EA7ozfUi44B'
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        
        # Sending the order to the external API
        response = requests.post(api_url, json=order_data, headers=headers)
        print("ok kyo")
        print(order_data)
        if response.status_code in [200, 201]:
            # request.session['pending_order']
           
            print("tayyab ka bosara 200")
            return JsonResponse({'status': 'success', 'message': 'Order placed successfully.'})

           
        else:
            print("order history in error")
            # Handle API error
            error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
            print(error_message)
            return {'status': 'error', 'message': error_message}
    except Exception as e:
        # If there's an error, return an error response with the error message
        error_message = str(e)
        return {'status': 'error', 'message': error_message}
@csrf_exempt
def send_order_to_printful_using_cart(request):
    items_for_api = []

    try:
        data = request.session.get('cart_order')
        print("from success")
        data=json.loads(data)
        print(data)
        name = data[0]['name']
        print(name)
        address = data[0]['address1']
        country = data[0]['country']
        city = data[0]['city']
        zip_code = data[0]['zip']
        recipient_details = {
    "name": name,
    "address1": address,
    "country": country,
    "city": city,
    "country_code": 'UK',
    "zip": zip_code
}
       
        for item in data[1]:
            print(item)
            variant_id = item['variantId']
            print(variant_id)
            price = item['price']
            print(price)
            image_url = item['imgSrc']
            
            print(image_url)
            items_for_api.append({
                    "variant_id": variant_id,
                    "quantity": 1,
                    "price": price,
                    "files": [{"type": "default", "url": image_url}]
                })
        order_data = {"recipient": recipient_details, "items": items_for_api}
        print("order data")
        print(order_data)
        
        if 'cart_order' in request.session:
            print("delete session")
            request.session.modified = True 
            del request.session['cart_order']
            
            

        send_order_to_printful_cart(order_data,request)
            



        if True:
         
            return {'status': 'success', 'message': 'Order placed successfully.'}
        else:
            # Handle API error
            error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
           
            return {'status': 'error', 'message': error_message}
    except Exception as e:
        # If there's an error, return an error response with the error message
        error_message = str(e)
        return {'status': 'error', 'message': error_message}
@csrf_exempt
def view_order_history(request):
    # Define the API endpoint URL
    api_url = 'https://api.printful.com/orders'

    # Set the authorization header with your API key
    headers = {'Authorization': 'Bearer hasiNeN7xTMlLWqhGQjxj053nGdD4EA7ozfUi44B'}

    # Make the GET request to the Printful API
    response = requests.get(api_url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Pass the response data to the template context
        context = {'orders': data}
        
        # Render the template with the order data in the context
        return render(request, 'order_history.html', context)
    else:
        # If the request was not successful, return an error message
        return HttpResponse("Error: Failed to fetch Printful orders")


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




def payment_form(request):
    return render(request, 'payment_form.html')
def cart_confirm_payment(request):
    return render(request, 'cart_confirm_payment.html')


def save_address_data(request):
    if request.method == 'POST':
        # Extract data from the POST request
        data = request.POST
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')
        zip_code = data.get('zip')

        # Process the data as needed
        # For example, save it to the database or perform other operations

        # Return a JSON response indicating success or failure
        return JsonResponse({'message': 'Address data received successfully.'})

    # Handle other HTTP methods if necessary
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
def retrive_data(request):
    imge_list = []  # Initialize a list to store image URLs
    data = json.loads(request.body)
    # Iterate over each item in the received items list
    for item in data.get('items', []):
        # Extract item details
        variant_id = item.get('variant_id')
        quantity = item.get('quantity')
        price = item.get('price')
        imge_list.append(item.get('image_url'))  # Append the image URL to the list
    return imge_list  # Return the list of image URLs




import stripe
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = 'home.html'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            print("Requwse")
            print(request)
            order_data_json = request.session.get('pending_order')
            print("from stripe")
            print(order_data_json)
            order_data_json=json.loads(order_data_json)
            variant_id = order_data_json['items'][0]['variant_id']
            quantity = int(order_data_json['items'][0]['quantity'])
            price = float(order_data_json['items'][0]['price'].split()[0])  # Extracting the numerical part of the price
            image_url = order_data_json['items'][0]['files'][0]['url']
          
            # Initialize the items list for the API request
           

            # Iterate over each item in the received items list
         

            # Create new Checkout Session for the order
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'payment-form/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'GBP',
                        'unit_amount': int(price)*100,  # Convert price to integer if needed
                        'product_data': {
                            'name': 'T-shirt',
                            'description': "NEW World Disorder",
                            'images': [image_url],  # Use the provided image_url
                        },
                    },
                    'quantity': quantity,
                }],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
@csrf_exempt
def create_checkout_session_cart(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            
            print("Requwse")
            print(request)
            order_cart_json = request.session.get('cart_order')
            print("from cart stripe")
            print(order_cart_json)
            order_cart_json=json.loads(order_cart_json)
            price = float(order_cart_json[2]['totalCost'].split()[0])  # Extracting the numerical part of the price
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'cart_confirm_payment/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'GBP',
                        'unit_amount': int(price)*100,  # Convert price to integer if needed
                        'product_data': {
                            'name': 'T-shirt',
                            'description': "NEW World Disorder",
                            'images': ["https://i.ibb.co/S36Gg4t/3081986.png"],  # Use the provided image_url
                        },
                    },
                    'quantity': 1,
                }],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})        

@csrf_exempt
def stripe_webhook(request):

    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # This method will be called when user successfully purchases something.
        handle_checkout_session(session)
        

    return HttpResponse(status=200)


def handle_checkout_session(session):
    # client_reference_id = user's id
    client_reference_id = session.get("client_reference_id")
    payment_intent = session.get("payment_intent")
    print("test")
    order_data_json = session.get('pending_order')
    print(order_data_json)

    if client_reference_id is None:
        # Customer wasn't logged in when purchasing
        return

    # Customer was logged in we can now fetch the Django user and make changes to our models
    try:
        user = User.objects.get(id=client_reference_id)
        print(user.username, "just purchased something.")
        # TODO: make changes to our models.
        

    except User.DoesNotExist:
        pass


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        
     
    return HttpResponse(status=200)

