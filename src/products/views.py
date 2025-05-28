from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg
from .models import Category, Brand, HardwareProduct, SoftwareProduct, ProductReview

class HomeView(TemplateView):
    template_name = 'products/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured products (both hardware and software)
        context['featured_hardware'] = HardwareProduct.objects.filter(
            featured=True, status='published'
        )[:8]
        context['featured_software'] = SoftwareProduct.objects.filter(
            featured=True, status='published'
        )[:8]
        context['categories'] = Category.objects.filter(parent=None)
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent=None)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get all subcategories including self
        category_ids = [category.id]
        subcategories = category.subcategories.all()
        if subcategories:
            category_ids.extend(subcategories.values_list('id', flat=True))
        
        # Get all products from this category and its subcategories
        context['hardware_products'] = HardwareProduct.objects.filter(
            category_id__in=category_ids,
            status='published'
        )
        context['software_products'] = SoftwareProduct.objects.filter(
            category_id__in=category_ids,
            status='published'
        )
        
        return context


class HardwareProductListView(ListView):
    model = HardwareProduct
    template_name = 'products/hardware_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = HardwareProduct.objects.filter(status='published')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by brand if provided
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(processor__icontains=search_query) |
                Q(memory__icontains=search_query) |
                Q(storage__icontains=search_query)
            )
        
        # Sort products
        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            # Default sorting by featured then name
            queryset = queryset.order_by('-featured', 'name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['product_type'] = 'hardware'
        context['current_category'] = self.request.GET.get('category', '')
        context['current_brand'] = self.request.GET.get('brand', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class SoftwareProductListView(ListView):
    model = SoftwareProduct
    template_name = 'products/software_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = SoftwareProduct.objects.filter(status='published')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by brand if provided
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Filter by license type
        license_type = self.request.GET.get('license')
        if license_type:
            queryset = queryset.filter(license_type=license_type)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(version__icontains=search_query) |
                Q(platform__icontains=search_query)
            )
        
        # Sort products
        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            # Default sorting by featured then name
            queryset = queryset.order_by('-featured', 'name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['license_types'] = dict(SoftwareProduct.LICENSE_TYPE_CHOICES)
        context['product_type'] = 'software'
        context['current_category'] = self.request.GET.get('category', '')
        context['current_brand'] = self.request.GET.get('brand', '')
        context['current_license'] = self.request.GET.get('license', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class HardwareProductDetailView(DetailView):
    model = HardwareProduct
    template_name = 'products/hardware_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get related products (same category, different product)
        context['related_products'] = HardwareProduct.objects.filter(
            category=product.category,
            status='published'
        ).exclude(id=product.id)[:4]
        
        # Get average rating
        reviews = product.reviews.all()
        context['reviews'] = reviews
        if reviews:
            context['avg_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
            context['review_count'] = reviews.count()
        else:
            context['avg_rating'] = 0
            context['review_count'] = 0
        
        return context


class SoftwareProductDetailView(DetailView):
    model = SoftwareProduct
    template_name = 'products/software_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get related products (same category, different product)
        context['related_products'] = SoftwareProduct.objects.filter(
            category=product.category,
            status='published'
        ).exclude(id=product.id)[:4]
        
        # Get average rating
        reviews = product.reviews.all()
        context['reviews'] = reviews
        if reviews:
            context['avg_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
            context['review_count'] = reviews.count()
        else:
            context['avg_rating'] = 0
            context['review_count'] = 0
        
        return context


class SearchResultsView(TemplateView):
    template_name = 'products/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            # Search both hardware and software products
            hardware_results = HardwareProduct.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(processor__icontains=query) |
                Q(memory__icontains=query) |
                Q(storage__icontains=query),
                status='published'
            )
            
            software_results = SoftwareProduct.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(version__icontains=query) |
                Q(platform__icontains=query),
                status='published'
            )
            
            context['hardware_results'] = hardware_results
            context['software_results'] = software_results
            context['query'] = query
            context['total_results'] = hardware_results.count() + software_results.count()
        
        return context
