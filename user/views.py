import csv
from django.contrib.auth.models import Permission
from django.http import JsonResponse, response
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)

from functools import wraps
from datetime import datetime, timedelta, date
import requests
import re
from bs4 import BeautifulSoup

from django.views.generic.base import View

from .search_query import Search
from .models import User
from .forms  import UserCreationFormFromView, UserEditFormFromView, UserEditFromFromProfile

strptime = datetime.strptime

#Decoradores
def is_logged_out(func):
	@wraps(func)
	def wrapper(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("/")

		return func(request, *args, **kwargs)

	return wrapper

# Create your views here.

@method_decorator(is_logged_out, name="dispatch")
class Login(View):
	def get(self, request):
		return render(
			request=request,
			template_name="user/login.html",
		)

	def post(self, request):
		err_user=None
		err_pass=None
		username = request.POST["username"]
		password = request.POST["password"]
		if User.objects.filter(username=username).exists():
			user = authenticate(
				username=username,
				password=password
			)
			if user is not None:
				login(request, user)
				return redirect(to=("/"))
			else:
				err_pass = "La contraseña es incorrecta"
		else:
			err_user = "El usuario no existe"
		return render(
			request=request,
			template_name="user/login.html",
			context={
				"err_user": err_user,
				"err_pass": err_pass
			}
		)

@method_decorator(login_required(login_url="/login/"), name="dispatch")
@method_decorator(permission_required("user.manage_users", login_url="/profile/"), name="dispatch")
class Home(View):
	def get(self, request):
		## Si la fecha y el termino estan vacias quitar las url queries
		if "search" not in request.GET and "f_inicio" not in request.GET and "f_fin" not in request.GET:
			pass
		elif not request.GET["search"] and not request.GET["f_inicio"] and not request.GET["f_fin"]:
			return redirect(to=("/"))

		default_page = 1
		page = request.GET.get('page', default_page)

		search = Search(request)
		search.makeQuery(request.GET)
		users = search.usuarios
		date_err = search.date_err

		items_per_page = 5
		paginator = Paginator(users, items_per_page)

		try:
			usuarios = paginator.page(page)
		except PageNotAnInteger:
			usuarios = paginator.page(default_page)
		except EmptyPage:
			usuarios = paginator.page(paginator.num_pages)

		get = request.GET
		url_params = ""

		if "search" in get:
			param = get["search"]
			url_params += f"&search={param}"

		if "filtro" in get:
			param = get["filtro"]
			url_params += f"&filtro={param}"

		if "f_inicio" in get:
			param = get["f_inicio"]
			url_params += f"&f_inicio={param}"

		if "f_fin" in get:
			param = get["f_fin"]
			url_params += f"&f_fin={param}"

		return render(
			request=request,
			template_name="user/home.html",
			context={
				"usuarios": usuarios,
				"date_err": date_err,
				"url_params": url_params
			}
		)

@method_decorator(login_required(login_url="/login/"), name="dispatch")
@method_decorator(permission_required("user.manage_users", login_url="/profile/"), name="dispatch")
class Create(View):
	def get(self, request):
		return render(
			request=request,
			template_name="user/create.html"
		)

	def post(self, request):
		form = UserCreationFormFromView(request.POST)

		if form.is_valid():
			user = User(
				username = form.cleaned_data["username"],
				email = form.cleaned_data["email"],
				first_name = form.cleaned_data["firstName"],
				last_name = form.cleaned_data["lastName"],
				registred_by = request.user,
				type = int(request.POST["tipo"]),
			)
			user.set_password(form.cleaned_data["password1"])
			user.save()

			p_manage_users = Permission.objects.get(codename="manage_users")
			p_change_credits = Permission.objects.get(codename="change_credits")

			if user.type == 2:
				user.user_permissions.set([p_manage_users, p_change_credits])

			if user.type == 3:
				user.user_permissions.add(p_manage_users)
		

			return redirect("/")
	
		values = {
		"firstName_value": request.POST["firstName"],
		"lastName_value": request.POST["lastName"],
		"username_value": request.POST["username"],
		"email_value": request.POST["email"],
		"password1_value": request.POST["password1"],
		"password2_value": request.POST["password2"],
		"tipo_value": request.POST["tipo"]
		}
		
		return render(
			request=request,
			template_name="user/create.html",
			context={
				**form.errors,
				**values
			}
		)

@method_decorator(login_required(login_url="/login/"), name="dispatch")
@method_decorator(permission_required("user.manage_users", login_url="/profile/"), name="dispatch")
class Delete(View):
	def get(self, request, username):
		user = get_object_or_404(User, username=username)

		# Si el usuario no existe, se redirige a la vista anterior
		if not user or user.registred_by != request.user:
			return redirect(request.META.get('HTTP_REFERER', '/'))

		user.delete()

		return redirect(request.META.get('HTTP_REFERER', '/'))
		
@method_decorator(login_required(login_url="/login/"), name="dispatch")
@method_decorator(permission_required("user.manage_users", login_url="/profile/"), name="dispatch")
class Edit(View):
	def get(self, request, username):
		user = get_object_or_404(User, username=username)

		values = {
			"firstName_value": user.first_name,
			"lastName_value": user.last_name,
			"username_value": user.username,
			"email_value": user.email,
			"is_active": user.is_active,
			"credits_value": user.credits,
			"registred_by_value": user.registred_by,
		}

		return render (
			request=request,
			template_name="user/edit.html",
			context={
			**values
			}
		)

	def post(self, request, username):
		user = get_object_or_404(User, username=username)
		form = UserEditFormFromView(data=request.POST, username2=user.username, email2=user.email)

		if form.is_valid():
			user.username = form.cleaned_data["username"]
			user.email = form.cleaned_data["email"]
			user.first_name = form.cleaned_data["firstName"]
			user.last_name = form.cleaned_data["lastName"]
			user.is_active = bool(request.POST.get("is_active", False))
			user.credits = int(form.cleaned_data["credits"])
			
			user.save()

			return redirect("/")

		values = {
			"firstName_value": user.first_name,
			"lastName_value": user.last_name,
			"username_value": user.username,
			"email_value": user.email,
			"credits_value": user.credits,
			"is_active": user.is_active,
			"registred_by_value": user.registred_by,
		}

		return render (
			request=request,
			template_name="user/edit.html",
			context={
			**values,
			**form.errors
			}
		)

@method_decorator(login_required(login_url="/login/"), name="dispatch")
class Profile(View):
	def get(self, request):
		user = request.user

		values = {
			"firstName_value": user.first_name,
			"lastName_value": user.last_name,
			"email_value": user.email,
		}

		return render(
			request=request,
			template_name="user/profile.html",
			context={
				**values
			}
		)

	def post(self, request):
		user = request.user
		form = UserEditFromFromProfile(data=request.POST, email2=request.user.email)
		success = None

		if form.is_valid():
			user.email = form.cleaned_data["email"]
			user.first_name = form.cleaned_data["firstName"]
			user.last_name = form.cleaned_data["lastName"]
			user.save()
			success = True

		values = {
			"firstName_value": user.first_name,
			"lastName_value": user.last_name,
			"email_value": user.email,
		}

		return render(
			request=request,
			template_name="user/profile.html",
			context={
			**values,
			**form.errors,
			"success": success
			}
		)

class Logout(View):
	def get(self, request):
		logout(request)
		return redirect("login")

@method_decorator(login_required(login_url="/login/"), name="dispatch")
@method_decorator(permission_required("user.manage_users", login_url="/profile/"), name="dispatch")
class export_to_csv(View):
	def get(self, request):
		response = HttpResponse(
			content_type="text/csv",
			headers={
				"Content-Disposition": 'attachment; filename="usuarios.csv"'
			}
		)

		writer = csv.writer(response)

		writer.writerow(["Username", "Email", "Nombre(s)", "Apellido(s)", "Creditós", "Activo", "Fecha de union", "Agregado por", "Tipo"])

		usuarios = User.objects.all()

		for usuario in usuarios:
			if usuario.type == 1:
				tipo = "Superuser"
			elif usuario.type == 2:
				tipo = "Administrador"
			elif usuario.type == 3:
				tipo = "Distribuidor"
			else:
				tipo = "Cliente"

			writer.writerow([usuario.username, usuario.email, usuario.first_name, usuario.last_name, str(usuario.credits), str(usuario.is_active), str(usuario.date_joined), str(usuario.registred_by), tipo])

		return response

@method_decorator(login_required(login_url="/login/"), name="dispatch")
class dollar_credits_api(View):
	def get(self, request):

		response = requests.get("https://www.google.com/search?q=1+usd+to+mxn")
		soup = BeautifulSoup(response.text, "html.parser")
		string = soup.find(class_="BNeawe iBp4i AP7Wnd").text
		usd = re.search(r'\d+\.\d+', string).group()

		data = {
			"USD": usd,
			"credits": request.user.credits
		}
		
		return JsonResponse(data=data)
