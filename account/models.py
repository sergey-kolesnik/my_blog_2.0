from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from services.utils import unique_slugify

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True, unique=True)
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="images/avatars/%Y/%m/%d/",
        default="images/avatars/default.png",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))]
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Информация о себе")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    

    class Meta:
        """
        Сортировка, название таблицы в базе данных
        """
        ordering = ("user")
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def save(self, *args, **kwargs):
        # pylint: disable=E1101
        """
        Сохранение полей модели при их отсуствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.user.username, self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        # pylint: disable=E1101
        """
        Возвращение строки
        """
        return str(self.user.username)


    def get_absolute_url(self):
        return reverse("profile_detai;l", kwargs={"slug": self.slug})
    

