# Generated by Django 4.1.3 on 2022-12-16 03:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=30, unique=True, verbose_name="usuario"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=255, unique=True, verbose_name="e-mail"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=50, verbose_name="nombre(s)"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=50, verbose_name="apellido(s)"),
                ),
                (
                    "credits",
                    models.PositiveIntegerField(default=0, verbose_name="créditos"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="activo")),
                (
                    "date_joined",
                    models.DateTimeField(auto_now_add=True, verbose_name="date joined"),
                ),
                (
                    "type",
                    models.PositiveBigIntegerField(
                        choices=[
                            (1, "Superusuario"),
                            (2, "Administrador"),
                            (3, "Distribuidor"),
                            (4, "Cliente"),
                        ]
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "registred_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="registred_users",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "manage_users",
                        "puede acceder a las vistas de gestión de usuarios",
                    ),
                    ("change_credits", "puede cambiar creditós de los usuarios"),
                ),
            },
        ),
    ]