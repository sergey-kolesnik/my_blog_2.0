from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """
    Модель категории товаров с поддержкой вложенных структур.
    Позволяет организовывать товары по категориям в виде дерева.

    Поля:
      * title — название категории
      * slug — короткий адрес категории для ссылок
      * description — краткое описание категории
      * parent — родительная категория (может быть пустой для корневых категорий)
    """

    title = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(max_length=255, verbose_name="URL категории", blank=True)
    description = models.TextField(verbose_name="Описание категории", max_length=300)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """

        order_insertion_by = ("title",)

    class Meta:
        """
        Настройки представления модели в администраторском интерфейсе.
        """

        verbose_name = "Категория"
        verbose_name_plural = "Категория"
        db_table = "app_categories"

    def __str__(self):
        """
        Представление категории в виде строки.
        Возвращает название категории.
        """
        return str(self.title)


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
    category = TreeForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="Категория",
    )
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
        default=1,
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
