from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import UserCreationForm, UserChangeForm

# Register your models here.
class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('first_name', 'last_name', 'username', 'email')
	readonly_fields = ('date_joined', 'registred_by')
	
	fieldsets = (
		('Información de usuario', {'fields': ('username', 'password', 'is_active', 'type', 'credits')}),
		('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
		('Permisos',
			{'fields': (
			'groups',
			'user_permissions')}),
		('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
		('Creación', {'fields': ('registred_by',)}),
	)

	add_fieldsets = (
		(None, {
			'classes' : ('wide',),
			'fields' : ('email', 'username', 'type', 'first_name', 'last_name' ,'password1', 'password2'),
		}),
	)
	
	list_filter = ('username',)
	filter_horizontal = ()

	def save_model(self, request, obj, form, change):
		if not obj.pk:
			obj.registred_by = request.user
		super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
