# Performance Tests

This section provides an overview of the performance tests conducted for the "New World Disorder" website. The tests were carried out using Lighthouse to evaluate key metrics such as Performance, Accessibility, Best Practices, and SEO.

## Performance Test Results

<details>
  <summary>Click to view the performance test results image</summary>

  ![Performance Test Results](https://github.com/Moodyw03/new-world-disorder/blob/main/static/test1.jpg?raw=true)

</details>

### Home Page
- **Performance**: 80
- **Accessibility**: 86
- **Best Practices**: 74
- **SEO**: 90

### /ch Page
- **Performance**: 90
- **Accessibility**: 86
- **Best Practices**: 74
- **SEO**: 70

### /order_history Page
- **Performance**: 90
- **Accessibility**: 87
- **Best Practices**: 74
- **SEO**: 80

### Observations
1. **Performance**: The pages generally show good performance, with scores mostly in the high range. The home page has a slightly lower score (80) due to initial load times influenced by serverless architecture and external API calls.
2. **Accessibility**: Scores are consistently high across all pages, indicating that the website is accessible to users with disabilities.
3. **Best Practices**: The scores suggest some improvements can be made in terms of following web development best practices.
4. **SEO**: The SEO scores are high, reflecting that the website is well-optimized for search engines.

### Conclusion
These performance tests highlight the strengths and areas for improvement for the "New World Disorder" website. The high scores in accessibility and SEO are particularly encouraging, indicating a user-friendly and search-engine-friendly site. Focus on optimizing best practices and performance further, especially for the home page, can enhance the overall user experience.

# CSS Validation Test

This section provides an overview of the CSS validation test conducted for the "New World Disorder" website. The test was carried out using the W3C CSS Validation Service to ensure that the website's stylesheets conform to the standards set by the World Wide Web Consortium (W3C).
<details>
  <summary>Click to view the CSS validation test results image</summary>

  ![CSS Validation Test Results](https://github.com/Moodyw03/new-world-disorder/blob/main/static/Screenshot%202024-05-22%20at%2011.21.40.png?raw=true)

</details>

### Observations
1. **Standards Compliance**: The validation results indicate that the website's CSS adheres to the W3C standards, ensuring cross-browser compatibility and maintainability.
2. **Errors and Warnings**: The test highlights any errors or warnings that need to be addressed to improve the overall quality and robustness of the stylesheets.

### Conclusion
The CSS validation test confirms that the "New World Disorder" website's stylesheets are well-formed and comply with industry standards. Addressing any highlighted errors or warnings will further enhance the website's presentation and functionality across different browsers and devices.



# User View Tests

The following tests verify the functionality of user authentication and profile management in the application. They cover scenarios including user login, logout, registration, profile viewing, and profile updating.

## Test Case: `TestUserViews`

This test case, `TestUserViews`, includes several tests to ensure the user-related views work as expected.

### Setup

Before running the tests, a test client and a user are created for use in the tests.

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TestUserViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

```

## Test: User Login
This test checks if a user can successfully log in.
```
    def test_user_login(self):
        response = self.client.post(reverse('login'), {'username_or_email': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check if login is successful (redirects)
```
## Test: User Logout
This test checks if a user can successfully log out.
```
    def test_user_logout(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Check if logout is successful (redirects)
```

## Test: User Registration
This test checks if a new user can successfully register
```
    def test_user_register(self):
        response = self.client.post(reverse('register'), {'username': 'newuser', 'email': 'new@example.com', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check if registration is successful (redirects)
```

## Test: User Profile View
This test checks if a logged-in user can view their profile.
```
    def test_user_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)  # Check if profile page loads successfully
```

## Test: Update Profile
```
    def test_update_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('update_profile'), {'username': 'updateduser', 'email': 'updated@example.com'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Check if profile update is successful

        # Check if the user object has been updated
        updated_user = User.objects.get(username='updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')
```
# Stripe Payment Integration Tests

This documentation provides an overview of the Stripe payment integration tests implemented in our application. The tests ensure that the payment process is correctly initialized and handled.

## Overview

The following JavaScript code integrates Stripe's payment elements into the application. It initializes the payment process, handles the submission of payment details, and manages the confirmation of payments.

![JavaScript Code for Stripe Integration](https://github.com/Moodyw03/new-world-disorder/blob/main/static/Screenshot%202024-05-21%20at%2021.44.25.png?raw=true)

# Python and Django (PEP 8) Compliance

I used the Code Institute PEP8 Validator to check that my Python code is PEP8 compliant. I validated any files that were either modified or created by me. Below is a table of the validated code, which shows the file validated, a screenshot, and a description of any warnings:

## Validated Code

<details>
  <summary>Click to view the screenshot of settings.py validation</summary>

  ![settings.py validation](https://github.com/Moodyw03/new-world-disorder/blob/main/static/settings%20test%20py.png?raw=true)

</details>

<details>
  <summary>Click to view the screenshot of tests.py validation</summary>

  ![tests.py validation](https://github.com/Moodyw03/new-world-disorder/blob/main/static/test%20tests%20py.png?raw=true)

</details>

| File          | Screenshot                                                                                             | Description of Warnings            |
|---------------|--------------------------------------------------------------------------------------------------------|------------------------------------|
| settings.py   | ![View Screenshot](https://github.com/Moodyw03/new-world-disorder/blob/main/static/settings%20test%20py.png?raw=true) | No warnings                        |
| tests.py      | ![View Screenshot](https://github.com/Moodyw03/new-world-disorder/blob/main/static/test%20tests%20py.png?raw=true)   | No warnings                        |

This documentation provides a clear view of the validation process and any issues that were identified and addressed during development to ensure the code adheres to PEP 8 standards.



### Initialization

The Stripe client is initialized with the publishable API key.

```javascript
var stripe = Stripe('pk_test_51IoWFQx8R99qnN14AgMtxKaSJeUEt01t4bKVWNKaevr8zbanpBfxvWc');
```

