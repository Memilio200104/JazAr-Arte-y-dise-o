from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase, Client, override_settings
from django.urls import reverse
from .models import CustomerProfile, ShippingAddress
from .services import register_customer, normalize_email, save_address, delete_address, set_default_address
from .tokens import make_verification_token, verify_email
from .limits import consume_limits


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', ACCOUNT_ORIGIN='https://testserver')
class AccountTests(TestCase):
    password = 'Prueba-Segura-74!solo-test'

    def setUp(self):
        self.customer = register_customer('Persona de prueba', 'client@example.com', self.password)

    def login(self):
        self.client.force_login(self.customer.user, backend='accounts.backends.CustomerEmailBackend')

    def address(self):
        return dict(recipient='Destinatario', phone='+52 55 1234 5678', street='Calle de prueba',
                    exterior='10', interior='', district='Centro', postcode='01234', city='Ciudad',
                    state='Ciudad de Mexico', reference='', label='Casa')

    def test_registration_identity(self):
        self.assertEqual(normalize_email(' A+tag@EXAMPLE.COM '), 'a+tag@example.com')
        self.assertTrue(self.customer.user.check_password(self.password))
        self.assertFalse(self.customer.user.is_staff)
        self.assertFalse(self.customer.user.is_superuser)
        self.assertIsNone(self.customer.default_address_id)
        with self.assertRaises(ValidationError):
            register_customer('Duplicado', 'CLIENT@example.com', self.password)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_admin_email_cannot_be_claimed(self):
        get_user_model().objects.create_user('admin-test', email='admin@example.com', is_staff=True)
        with self.assertRaises(ValidationError):
            register_customer('Otro', 'ADMIN@example.com', self.password)

    def test_register_post_and_email(self):
        r = self.client.post('/cuenta/registro/', {'full_name':'Nueva Persona','email':'new@example.com',
                            'password1':self.password,'password2':self.password})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox),1)
        self.assertIsNone(CustomerProfile.objects.get(email='new@example.com').email_verified_at)

    def test_bad_password(self):
        r = self.client.post('/cuenta/registro/', {'full_name':'Otro','email':'new@example.com',
                            'password1':'123','password2':'123'})
        self.assertEqual(r.status_code,200)
        self.assertFalse(CustomerProfile.objects.filter(email='new@example.com').exists())

    def test_password_spaces_preserved(self):
        from .forms import RegistrationForm, LoginForm
        password = ' ' + self.password + ' '
        for field in [RegistrationForm().fields['password1'], RegistrationForm().fields['password2'], LoginForm().fields['password']]:
            self.assertEqual(field.clean(password), password)

    def test_write_failures_are_recoverable(self):
        from django.db import OperationalError
        self.login()
        address = save_address(self.customer, self.address())
        with patch('accounts.views.NameForm.save', side_effect=OperationalError):
            self.assertContains(self.client.post('/cuenta/', {'full_name':'Nuevo'}), 'Inténtalo de nuevo')
        with patch('accounts.views.delete_address', side_effect=OperationalError):
            self.assertContains(self.client.post(f'/cuenta/direcciones/{address.pk}/eliminar/'), 'Inténtalo de nuevo')
        with patch('accounts.views.set_default_address', side_effect=OperationalError):
            self.assertContains(self.client.post(f'/cuenta/direcciones/{address.pk}/predeterminada/', follow=True), 'Inténtalo de nuevo')
        self.assertTrue(ShippingAddress.objects.filter(pk=address.pk).exists())

    def test_login_and_safe_next(self):
        r = self.client.post('/cuenta/ingresar/?next=https://evil.example/',
                            {'email':'CLIENT@example.com','password':self.password})
        self.assertRedirects(r,'/cuenta/')
        self.assertContains(self.client.get('/cuenta/'), 'Persona de prueba')
        self.assertEqual(self.client.get('/cuenta/salir/').status_code,405)
        self.assertEqual(self.client.post('/cuenta/salir/').status_code,302)
        self.assertEqual(self.client.get('/cuenta/').status_code,302)

    def test_inactive_and_admin_cannot_enter_customer_account(self):
        self.customer.user.is_active=False
        self.customer.user.save()
        r=self.client.post('/cuenta/ingresar/',{'email':self.customer.email,'password':self.password})
        self.assertEqual(r.status_code,200)
        self.assertNotIn('_auth_user_id',self.client.session)
        admin=get_user_model().objects.create_user('staff',password=self.password,is_staff=True)
        self.client.force_login(admin)
        self.assertEqual(self.client.get('/cuenta/').status_code,403)

    def test_csrf_required(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post('/cuenta/ingresar/',{}).status_code,403)

    def test_account_private_and_name_edit(self):
        self.login()
        r=self.client.post('/cuenta/',{'full_name':'Nombre <nuevo>'})
        self.assertEqual(r.status_code,302)
        r=self.client.get('/cuenta/')
        self.assertContains(r,'Nombre &lt;nuevo&gt;')
        self.assertIn('no-store',r.headers['Cache-Control'])

    def test_orders_primary_link(self):
        self.login()
        self.assertContains(self.client.get('/cuenta/'), '<a class="button button-primary" href="/cuenta/pedidos/">Mis pedidos <i data-lucide="package" aria-hidden="true"></i></a>', html=True)

    def test_address_defaults(self):
        a=save_address(self.customer,self.address())
        b=save_address(self.customer,{**self.address(),'label':'Otra'})
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.default_address_id,a.pk)
        set_default_address(self.customer,b.pk)
        delete_address(self.customer,b.pk)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.default_address_id,a.pk)
        delete_address(self.customer,a.pk)
        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.default_address_id)

    def test_other_address_is_private(self):
        other=register_customer('Otra','other@example.com',self.password)
        a=save_address(other,self.address())
        self.login()
        for action in ['editar','eliminar','predeterminada']:
            self.assertEqual(self.client.post(f'/cuenta/direcciones/{a.pk}/{action}/',self.address()).status_code,404)
        self.assertTrue(ShippingAddress.objects.filter(pk=a.pk).exists())

    def test_address_validation_and_delete_confirmation(self):
        self.login()
        r=self.client.post('/cuenta/direcciones/nueva/',{**self.address(),'postcode':'1234'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(ShippingAddress.objects.count(),0)
        self.client.post('/cuenta/direcciones/nueva/',self.address())
        a=ShippingAddress.objects.get()
        self.assertEqual(a.postcode,'01234')
        self.assertEqual(self.client.get(f'/cuenta/direcciones/{a.pk}/eliminar/').status_code,200)
        self.assertTrue(ShippingAddress.objects.filter(pk=a.pk).exists())

    def test_verification_requires_post_and_is_single_use(self):
        token=make_verification_token(self.customer)
        url=reverse('verify_email',args=[token])
        self.assertEqual(self.client.get(url).status_code,200)
        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.email_verified_at)
        self.assertEqual(self.client.post(url).status_code,200)
        self.customer.refresh_from_db()
        self.assertIsNotNone(self.customer.email_verified_at)
        self.assertFalse(verify_email(token))

    def test_expired_verification(self):
        with patch('django.core.signing.time.time',return_value=1):
            token=make_verification_token(self.customer)
        self.assertFalse(verify_email(token))

    def test_reset_generic_and_scope(self):
        known=self.client.post('/cuenta/recuperar/',{'email':self.customer.email})
        unknown=self.client.post('/cuenta/recuperar/',{'email':'unknown@example.com'})
        self.assertEqual(known.url,unknown.url)
        self.assertEqual(len(mail.outbox),1)
        get_user_model().objects.create_user('staff',email='staff@example.com',password=self.password)
        self.client.post('/cuenta/recuperar/',{'email':'staff@example.com'})
        self.assertEqual(len(mail.outbox),1)

    def test_limit(self):
        for _ in range(3):
            self.assertTrue(consume_limits('recovery','127.0.0.1',self.customer.email)[0])
        allowed,retry=consume_limits('recovery','127.0.0.1',self.customer.email)
        self.assertFalse(allowed)
        self.assertGreater(retry,0)

    def test_malformed_next_does_not_crash(self):
        r=self.client.post('/cuenta/ingresar/?next=//[invalid',{'email':self.customer.email,'password':self.password})
        self.assertRedirects(r,'/cuenta/')

    def test_limit_expires(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import AuthAttemptBucket
        for _ in range(3):
            consume_limits('recovery','127.0.0.1',self.customer.email)
        AuthAttemptBucket.objects.update(started_at=timezone.now()-timedelta(seconds=901))
        self.assertTrue(consume_limits('recovery','127.0.0.1',self.customer.email)[0])

    def test_reset_token_consumed_and_old_session_revoked(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        self.login()
        token=default_token_generator.make_token(self.customer.user)
        uid=urlsafe_base64_encode(force_bytes(self.customer.user.pk))
        reset_client=Client()
        response=reset_client.get(reverse('password_reset_confirm',args=[uid,token]))
        self.assertEqual(response.status_code,302)
        reset_url=response.url
        new_password=' Nueva-Segura-91!test '
        response=reset_client.post(reset_url,{'new_password1':new_password,'new_password2':new_password})
        self.assertEqual(response.status_code,302)
        self.customer.user.refresh_from_db()
        self.assertTrue(self.customer.user.check_password(new_password))
        self.assertFalse(default_token_generator.check_token(self.customer.user,token))
        self.assertEqual(self.client.get('/cuenta/').status_code,302)
        self.assertRedirects(reset_client.post('/cuenta/ingresar/',{'email':self.customer.email,'password':new_password}),'/cuenta/')

    def test_verification_csrf_and_wrong_email(self):
        token=make_verification_token(self.customer)
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse('verify_email',args=[token])).status_code,403)
        CustomerProfile.objects.filter(pk=self.customer.pk).update(email='changed@example.com')
        self.assertFalse(verify_email(token))

    def test_limit_storage_failure_closed(self):
        from django.db import OperationalError
        with patch('accounts.views.consume_limits',side_effect=OperationalError):
            self.assertEqual(self.client.post('/cuenta/ingresar/',{}).status_code,503)

    def test_mail_failure_preserves_pending_account(self):
        with patch('accounts.mail.EmailMessage.send',side_effect=OSError):
            r=self.client.post('/cuenta/registro/',{'full_name':'Nueva','email':'new@example.com',
                'password1':self.password,'password2':self.password})
        self.assertEqual(r.status_code,302)
        self.assertIsNone(CustomerProfile.objects.get(email='new@example.com').email_verified_at)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ConcurrentRegistrationTests(TransactionTestCase):
    def test_same_email_concurrent_registration_has_no_orphan_user(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from time import sleep
        from django.db import connections, OperationalError
        barrier=Barrier(2)

        def worker():
            barrier.wait()
            try:
                for attempt in range(10):
                    try:
                        register_customer('Persona','same@example.com','Prueba-Segura-74!test')
                        return 'created'
                    except ValidationError:
                        return 'duplicate'
                    except OperationalError:
                        sleep(.03*(attempt+1))
                return 'busy'
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results=list(executor.map(lambda _:worker(), range(2)))
        self.assertEqual(sorted(results),['created','duplicate'])
        self.assertEqual(CustomerProfile.objects.count(),1)
        self.assertEqual(get_user_model().objects.count(),1)
