from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User


class Post(models.Model):
    """
    Модель постов для блога
    """

    STATUS_OPTIONS = (
        ("published", "Опубликованно"),
        ("draft", "Черновик"),
    )

    title = models.CharField(verbose_name="Название поста", max_length=255)
    slug = models.SlugField(verbose_name="URL", max_length=255, blank=True, unique=True)
    descriotion = models.TextField(verbose_name="Краткое описание", max_length=500)
    text = models.TextField(verbose_name="Содержание поста")
    thumbnail = models.ImageField(
        default="default.jpg",
        verbose_name="Изображение поста",
        blank=True,
        upload_to="images/thumbnails/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=("png", "jpg", "webp", "jpeg", "gif")
            )
        ],
    )
    status = models.CharField(
        choices=STATUS_OPTIONS,
        default="published",
        verbose_name="Статус записи",
        max_length=10,
    )
    create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    author = models.ForeignKey(
        to=User,
        verbose_name="Автор",
        on_delete=models.SET_DEFAULT,
        related_name="author_posts",
    )
    updater = models.ForeignKey(
        to=User,
        verbose_name="Обновил",
        on_delete=models.SET_NULL,
        null=True,
        related_name="updater_posts",
        blank=True,
    )
    fixed = models.BooleanField(verbose_name="Прикреплено", default=False)

    class Meta:
        db_table = "blog_post"
        ordering = ["-fixed", "-create"]
        indexes = [models.Index(fields=["-fixed", "-create", "status"])]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return str(self.title)
