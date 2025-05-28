from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BaseProduct(models.Model):
    """Base abstract model for all product types"""
    PRODUCT_TYPE_CHOICES = (
        ('hardware', 'Hardware'),
        ('software', 'Software'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='%(class)s_products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='%(class)s_products')
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price


class HardwareProduct(BaseProduct):
    """Physical hardware products like phones, laptops, etc."""
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('refurbished', 'Refurbished'),
        ('used', 'Used'),
    )
    
    quantity = models.PositiveIntegerField(default=0)
    warranty_months = models.PositiveIntegerField(default=0, help_text="Warranty duration in months")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True, help_text="Format: LxWxH in cm")
    color = models.CharField(max_length=50, blank=True)
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES, default='new')
    
    # Specific fields for electronics
    processor = models.CharField(max_length=100, blank=True, null=True)
    memory = models.CharField(max_length=50, blank=True, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    display = models.CharField(max_length=100, blank=True, null=True)
    battery_life = models.CharField(max_length=50, blank=True, null=True)
    camera = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_type = 'hardware'
    
    @property
    def in_stock(self):
        return self.quantity > 0


class SoftwareProduct(BaseProduct):
    """Digital software products"""
    LICENSE_TYPE_CHOICES = (
        ('perpetual', 'Perpetual'),
        ('subscription', 'Subscription'),
        ('freemium', 'Freemium'),
        ('open_source', 'Open Source'),
    )
    
    VERSION_CHOICES = (
        ('standard', 'Standard'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
        ('ultimate', 'Ultimate'),
    )
    
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES)
    version = models.CharField(max_length=50)
    edition = models.CharField(max_length=20, choices=VERSION_CHOICES, blank=True, null=True)
    platform = models.CharField(max_length=100, help_text="Compatible platforms: Windows, Mac, Linux, etc.")
    download_link = models.URLField(blank=True, null=True)
    activation_key_required = models.BooleanField(default=True)
    subscription_period = models.PositiveIntegerField(blank=True, null=True, help_text="Period in months if subscription-based")
    system_requirements = models.TextField(blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_type = 'software'
    
    @property
    def in_stock(self):
        # Software is typically always in stock
        return self.status == 'published'


class ProductImage(models.Model):
    """Images for both hardware and software products"""
    hardware_product = models.ForeignKey(HardwareProduct, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    software_product = models.ForeignKey(SoftwareProduct, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['is_primary', 'created_at']
    
    def __str__(self):
        product = self.hardware_product or self.software_product
        return f"Image for {product.name} ({'primary' if self.is_primary else 'secondary'})"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure either hardware_product or software_product is set, but not both
        if not self.hardware_product and not self.software_product:
            raise ValidationError('An image must be associated with either a hardware or software product')
        if self.hardware_product and self.software_product:
            raise ValidationError('An image cannot be associated with both hardware and software products')


class ProductReview(models.Model):
    """Reviews for both hardware and software products"""
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    hardware_product = models.ForeignKey(HardwareProduct, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    software_product = models.ForeignKey(SoftwareProduct, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        product = self.hardware_product or self.software_product
        return f"{self.rating}-star review by {self.user.username} for {product.name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure either hardware_product or software_product is set, but not both
        if not self.hardware_product and not self.software_product:
            raise ValidationError('A review must be associated with either a hardware or software product')
        if self.hardware_product and self.software_product:
            raise ValidationError('A review cannot be associated with both hardware and software products')
