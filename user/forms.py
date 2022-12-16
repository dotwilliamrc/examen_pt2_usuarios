from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
import re

from django.shortcuts import get_object_or_404

from .models import User

from .models import User

class UserCreationForm(forms.ModelForm):
	password1 = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="La contraseña no puede tener espacios en blanco."),
			validators.RegexValidator(regex=r"^([0-9!@#$^&*()\-_=+{};:,.]+)$",message="La contraseña únicamenten debe de contener números y caracteres especiales."),
			validators.RegexValidator(regex=r"^(?=(?:.*\d))(?=(?:.*[!@#$^&*()\-_=+{};:,.])).+$",message="La contraseña debe tener al menos un numero y caracter especial entre: !@#$^&*()\-_=+{};:,."),
			validators.RegexValidator(regex=r".{10,}",message="La contraseña debe tener al menos 10 caracteres"),
		],
		label="Contraseña",
		widget=forms.PasswordInput
	)
	password2 = forms.CharField(
		label="Repite la contraseña",
		widget=forms.PasswordInput
	)

	class Meta:
		model = User	
		fields = ("username", "email", "first_name", "last_name")

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise ValidationError("Las contraseñas no coinciden.")
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ("username", "email", "first_name", "last_name", "credits")

	def clean_password(self):
		return self.initial["password"]

class UserCreationFormFromView(forms.Form):
	firstName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	lastName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	username = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="El username no puede tener espacios en blanco."),
		],
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
				"placeholder": "Username"
			}
		),
		required=True
	)

	email = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="El email no puede tener espacios en blanco."),
			validators.RegexValidator(regex=r"^(.+)(\@)(\w+)(\.)(\w{3,4})$",message="El email no es válido.")
		],
		widget=forms.EmailInput(
			attrs={
				"class": "form-control",
				"placeholder": "tu@ejemplo.com"
			}
		),
		required=True
	)

	password1 = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="La contraseña no puede tener espacios en blanco."),
			validators.RegexValidator(regex=r"^([0-9!@#$^&*()\-_=+{};:,.]+)$",message="La contraseña únicamenten debe de contener números y caracteres especiales."),
			validators.RegexValidator(regex=r"^(?=(?:.*\d))(?=(?:.*[!@#$^&*()\-_=+{};:,.])).+$",message="La contraseña debe tener al menos un numero y caracter especial entre: !@#$^&*()\-_=+{};:,."),
			validators.RegexValidator(regex=r".{10,}",message="La contraseña debe tener al menos 10 caracteres"),
		],
		widget=forms.PasswordInput(
			attrs={
				"class": "form-control",
				"placeholder": "Contraseña"
			}
		),
		required=True
	)

	password2 = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
				"class": "form-control",
				"placeholder": "Contraseña"
			}
		),
		required=True
	)

	def clean_username(self):
		username = self.cleaned_data.get("username")
		try:
			user = User.objects.get(username=username)
			raise ValidationError("El usuario ya existe.")
		except User.DoesNotExist:
			pass
		return username

	def clean_email(self):
		email = self.cleaned_data.get("email")
		try:
			user = User.objects.get(email=email)
			raise ValidationError("El email ya esta registrado.")
		except User.DoesNotExist:
			pass
		return email

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise ValidationError("Las contraseñas no coinciden.")
		return password2

class UserEditFormFromView(forms.Form):
	firstName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	lastName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	username = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="El username no puede tener espacios en blanco."),
		],
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
				"placeholder": "Username"
			}
		),
		required=True
	)

	email = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="El email no puede tener espacios en blanco."),
			validators.RegexValidator(regex=r"^(.+)(\@)(\w+)(\.)(\w{3,4})$",message="El email no es válido.")
		],
		widget=forms.EmailInput(
			attrs={
				"class": "form-control",
				"placeholder": "tu@ejemplo.com"
			}
		),
		required=True
	)

	credits = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^(0|[1-9]\d*)$", message="Numero invalido.")
		],
		widget=forms.NumberInput(),
		required=True
	)

	def __init__(self, *args, **kwargs):
		username2 = kwargs.pop('username2', None)
		email2 = kwargs.pop('email2', None)
		super().__init__(*args, **kwargs)
		self.username2 = username2
		self.email2 = email2

	def clean_username(self):
		username = self.cleaned_data.get("username")
		username2 = self.username2
		if username != username2:
			try:
				user = User.objects.get(username=username)
				raise ValidationError("El usuario ya existe.")
			except User.DoesNotExist:
				pass
		return username

	def clean_email(self):
		email = self.cleaned_data.get("email")
		email2 = self.email2
		if email != email2:
			try:
				user = User.objects.get(email=email)
				raise ValidationError("El email ya esta registrado.")
			except User.DoesNotExist:
				pass
		return email

class UserEditFromFromProfile(forms.Form):
	firstName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	lastName = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"class": "form-control",
			}
		),
		required=True
	)

	email = forms.CharField(
		validators=[
			validators.RegexValidator(regex=r"^\S+$",message="El email no puede tener espacios en blanco."),
			validators.RegexValidator(regex=r"^(.+)(\@)(\w+)(\.)(\w{3,4})$",message="El email no es válido.")
		],
		widget=forms.EmailInput(
			attrs={
				"class": "form-control",
				"placeholder": "tu@ejemplo.com"
			}
		),
		required=True
	)

	def __init__(self, *args, **kwargs):
		email2 = kwargs.pop('email2', None)
		super().__init__(*args, **kwargs)
		self.email2 = email2


	def clean_email(self):
		email = self.cleaned_data.get("email")
		email2 = self.email2
		if email != email2:
			try:
				user = User.objects.get(email=email)
				raise ValidationError("El email ya esta registrado.")
			except User.DoesNotExist:
				pass
		return email
