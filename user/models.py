from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission, PermissionsMixin
from django.conf import settings
Usr = settings.AUTH_USER_MODEL

# Create your models here.
class UserManager(BaseUserManager):
	def _create_user(self, email, password, **extra_fields):

		if not email:
				raise ValueError('Los usuarios deben tener un email')

		email = self.normalize_email(email)

		user = self.model(
			email=email,
			**extra_fields
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		return self._create_user(
			email,
			password,
			**extra_fields
		)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('type', 1)
		
		if extra_fields.get('type') is not 1:
			raise ValueError('Superuser debe tener type=1')

		return self._create_user(
			email,
			password,
			**extra_fields
		)

class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(
		verbose_name="usuario",
		max_length=30,
		unique=True
	)
	email = models.EmailField(
		verbose_name="e-mail",
		max_length=255,
		unique=True
	)
	first_name = models.CharField(
		verbose_name="nombre(s)",
		max_length=50,
	)
	last_name = models.CharField(
		verbose_name="apellido(s)",
		max_length=50,
	)
	credits = models.PositiveIntegerField(
		verbose_name='créditos',
		default=0
	)
	is_active = models.BooleanField(
		verbose_name="activo",
		default=True
	)

	date_joined = models.DateTimeField(
		verbose_name='date joined',
		auto_now_add=True
	)

	registred_by = models.ForeignKey(
		to=Usr,
		on_delete=models.SET_NULL,
		related_name="registred_users",
		null=True,
		blank=True
	)

	type = models.PositiveBigIntegerField(
		choices=(
			(1, 'Superusuario'),
			(2, 'Administrador'),
			(3, 'Distribuidor'),
			(4, 'Cliente'),
		)
	)

	objects = UserManager()

	USERNAME_FIELD = "username"
	REQUIRED_FIELDS = ["email", "first_name", "last_name", "type"]

	class Meta:
		permissions = (
			("manage_users", "puede acceder a las vistas de gestión de usuarios"),
			("change_credits", "puede cambiar creditós de los usuarios"),

		)

	def __str__(self):
		return self.username

	@property
	def is_staff(self):
		if self.type == 1:
			return True
		else:
			return False

	@property
	def is_superuser(self):
		if self.type == 1:
			return True
		else:
			return False


