from django.db.models import Q
from datetime import datetime, timedelta
from .models import User

strptime = datetime.strptime


class Search:
	def __init__(self, request):
		self.request = request

	def makeQuery(self, GET):
		## Lista para guardar todas las queries de los filtors despues
		queries = []

		## Declarar una valiable para guardar un error de los filtros si es que los hay
		self.date_err = None

		## Verificar si hay algun termino de busqueda en el input y agregarlo a la query
		if GET.get("search", False):
			search = GET["search"]
			if GET["filtro"] == "1":
				queries.append((Q(first_name__contains=search) | Q(last_name__contains=search)))
			else:
				queries.append(Q(email__contains=search))

		## Verificar si hay filtro de rango de fechas
		## Si hay un error guardarlo para mostrarlo despues
		f_inicio = GET.get("f_inicio", False)
		f_fin = GET.get("f_fin", False)

		if f_inicio and f_fin:

			if strptime(f_inicio, "%Y-%m-%d") < strptime(f_fin, "%Y-%m-%d") -timedelta(days=1):
				queries.append(Q(date_joined__range=[f_inicio, f_fin]))
			else:
				self.date_err = "Rango de fechas erróneo."

		## Si hay un error guardarlo para mostrarlo despues.
		if not f_inicio and f_fin or f_inicio and not f_fin:
			self.date_err = "Debes definir las 2 fechas."

		## Mostrar la query dependiendo del nivel de usuaro.
		if self.request.user.type <= 2:
			self.usuarios = User.objects.filter(*queries).exclude(Q(type=1) | Q(username=self.request.user.username))
		else:
			self.usuarios = User.objects.filter(type=4, registred_by=self.request.user, *queries)
