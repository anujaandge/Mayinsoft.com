from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Contact, Order, OrderUpdate
from datetime import datetime

class ShopViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            product_name="Test Product",
            desc="Test Description",
            category="Test Category",
            price=100,
            pub_date=datetime.now()  # Add pub_date field
        )
        self.contact = Contact.objects.create(
            name="Test User",
            email="test@example.com",
            phone="1234567890",
            desc="Test Message"
        )
        self.order = Order.objects.create(
            items_json="{}",
            name="Test User",
            email="test@example.com",
            phone="1234567890",
            address="Test Address",
            city="Test City",
            state="Test State",
            zip_code="123456",
            amount=100
        )
        self.order_update = OrderUpdate.objects.create(
            order_id=self.order.order_id,
            update_desc="Test Update"
        )

    def test_index_view(self):
        response = self.client.get(reverse('ShopHome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_about_view(self):
        response = self.client.get(reverse('AboutUs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/about.html')

    def test_contact_view(self):
        response = self.client.get(reverse('ContactUs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/contact.html')

    def test_contact_success_view(self):
        response = self.client.get(reverse('contact_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/contact_success.html')

    def test_tracker_view(self):
        response = self.client.get(reverse('TrackingStatus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/tracker.html')

    def test_search_view(self):
        response = self.client.get(reverse('Search'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/search.html')

    def test_product_view(self):
        response = self.client.get(reverse('ProductView', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/prodView.html')

    def test_checkout_view(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/checkout.html')

    # def test_checkout_success_view(self):
    #     response = self.client.get(reverse('checkout_success'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'shop/checkout_success.html')
