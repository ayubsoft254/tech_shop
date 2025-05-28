from django.contrib import admin
from .models import (
    Category, 
    Brand, 
    HardwareProduct, 
    SoftwareProduct,
    ProductImage, 
    ProductReview
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary')


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't show empty forms


class HardwareProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'sale_price', 
                   'quantity', 'status', 'featured')
    list_filter = ('status', 'featured', 'brand', 'category', 'condition')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'category', 'brand', 'featured')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'sale_price', 'status', 'quantity')
        }),
        ('Physical Attributes', {
            'fields': ('condition', 'weight', 'dimensions', 'color', 'warranty_months')
        }),
        ('Technical Specifications', {
            'fields': ('processor', 'memory', 'storage', 'display', 'battery_life', 
                      'camera', 'operating_system', 'release_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProductImageInline, ProductReviewInline]


class SoftwareProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'sale_price', 
                   'license_type', 'version', 'status', 'featured')
    list_filter = ('status', 'featured', 'brand', 'category', 'license_type', 'edition')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'category', 'brand', 'featured')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'sale_price', 'status')
        }),
        ('Software Details', {
            'fields': ('license_type', 'version', 'edition', 'platform', 
                      'download_link', 'activation_key_required', 'subscription_period')
        }),
        ('Additional Information', {
            'fields': ('system_requirements', 'release_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProductImageInline, ProductReviewInline]


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'alt_text', 'is_primary', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('alt_text', 'hardware_product__name', 'software_product__name')
    
    def get_product_name(self, obj):
        return obj.hardware_product.name if obj.hardware_product else obj.software_product.name
    get_product_name.short_description = 'Product'
    get_product_name.admin_order_field = 'hardware_product__name'


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'user', 'rating', 'title', 'verified_purchase', 'created_at')
    list_filter = ('rating', 'verified_purchase', 'created_at')
    search_fields = ('title', 'comment', 'user__username', 'hardware_product__name', 'software_product__name')
    readonly_fields = ('created_at',)
    
    def get_product_name(self, obj):
        return obj.hardware_product.name if obj.hardware_product else obj.software_product.name
    get_product_name.short_description = 'Product'
    get_product_name.admin_order_field = 'hardware_product__name'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(HardwareProduct, HardwareProductAdmin)
admin.site.register(SoftwareProduct, SoftwareProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
