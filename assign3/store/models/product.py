"""
Product Models - All product-related models for the bookstore application.
Contains: Category, Book, BookDetail, BookImage, Author, Translator, 
         Publisher, Language, BookFormat, Series, Tag, BookTag
"""
from django.db import models
from store.models.base import TimeStampedModel


class Category(TimeStampedModel):
    """
    Category Model - Represents book categories/genres.
    Supports hierarchical structure with parent categories.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Return full category path (e.g., 'Fiction > Mystery > Crime')."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Author(TimeStampedModel):
    """
    Author Model - Represents book authors.
    """
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'store_author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        ordering = ['name']

    def __str__(self):
        return self.name


class Translator(TimeStampedModel):
    """
    Translator Model - Represents book translators.
    """
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='translators/', blank=True, null=True)

    class Meta:
        db_table = 'store_translator'
        verbose_name = 'Translator'
        verbose_name_plural = 'Translators'
        ordering = ['name']

    def __str__(self):
        return self.name


class Publisher(TimeStampedModel):
    """
    Publisher Model - Represents book publishers.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='publishers/', blank=True, null=True)

    class Meta:
        db_table = 'store_publisher'
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Language(TimeStampedModel):
    """
    Language Model - Represents book languages.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # e.g., 'en', 'vi', 'fr'

    class Meta:
        db_table = 'store_language'
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'
        ordering = ['name']

    def __str__(self):
        return self.name


class BookFormat(TimeStampedModel):
    """
    Book Format Model - Represents book formats (Hardcover, Paperback, Ebook, etc.).
    """
    FORMAT_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-Book'),
        ('audiobook', 'Audiobook'),
        ('spiral', 'Spiral Bound'),
    ]

    name = models.CharField(max_length=50, choices=FORMAT_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_book_format'
        verbose_name = 'Book Format'
        verbose_name_plural = 'Book Formats'

    def __str__(self):
        return self.get_name_display()


class Series(TimeStampedModel):
    """
    Series Model - Represents book series (e.g., Harry Potter series).
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_books = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_series'
        verbose_name = 'Series'
        verbose_name_plural = 'Series'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    """
    Tag Model - Represents tags for books (for flexible categorization).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'store_tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(TimeStampedModel):
    """
    Book Model - Represents a book in the bookstore inventory.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    
    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    translator = models.ForeignKey(
        Translator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    book_format = models.ForeignKey(
        BookFormat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    series = models.ForeignKey(
        Series,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    series_order = models.IntegerField(blank=True, null=True)
    
    # Additional fields
    publication_date = models.DateField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='books/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_in_stock(self):
        """Check if book is available in stock."""
        return self.stock_quantity > 0

    def reduce_stock(self, quantity):
        """Reduce stock quantity after purchase."""
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock quantity")
        self.stock_quantity -= quantity
        self.save()

    def add_stock(self, quantity):
        """Add stock quantity."""
        self.stock_quantity += quantity
        self.save()

    def get_discount_percentage(self):
        """Calculate discount percentage."""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class BookDetail(TimeStampedModel):
    """
    Book Detail Model - Extended specifications for books (OneToOne with Book).
    """
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='detail'
    )
    pages = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # in grams
    dimensions = models.CharField(max_length=100, blank=True, null=True)  # e.g., "20x15x2 cm"
    edition = models.CharField(max_length=100, blank=True, null=True)
    binding_type = models.CharField(max_length=100, blank=True, null=True)
    paper_type = models.CharField(max_length=100, blank=True, null=True)
    age_group = models.CharField(max_length=50, blank=True, null=True)
    table_of_contents = models.TextField(blank=True, null=True)
    sample_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_book_detail'
        verbose_name = 'Book Detail'
        verbose_name_plural = 'Book Details'

    def __str__(self):
        return f"Details of {self.book.title}"


class BookImage(TimeStampedModel):
    """
    Book Image Model - Multiple images for books (ForeignKey to Book).
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='book_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_book_image'
        verbose_name = 'Book Image'
        verbose_name_plural = 'Book Images'
        ordering = ['display_order']

    def __str__(self):
        return f"Image for {self.book.title}"


class BookTag(TimeStampedModel):
    """
    Book Tag Model - ManyToMany intermediate table between Book and Tag.
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='book_tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='book_tags'
    )

    class Meta:
        db_table = 'store_book_tag'
        verbose_name = 'Book Tag'
        verbose_name_plural = 'Book Tags'
        unique_together = ['book', 'tag']

    def __str__(self):
        return f"{self.book.title} - {self.tag.name}"
