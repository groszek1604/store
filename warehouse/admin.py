from django.contrib import admin, messages
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models import Count
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models
from tags.models import TaggedItem

INVENTORY_STATUS = {'LOW': '<5',
                    'STABLE': '>5'
                    }

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (INVENTORY_STATUS['LOW'], 'Low'),
            (INVENTORY_STATUS['STABLE'], 'Stable')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<5':
            return queryset.filter(inventory__lt=5)
        else:
            return queryset.filter(inventory__gt=5)


class TagInLine(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    search_fields = ['product']
    actions = ['clear_inventory']
    inlines = [TagInLine]
    list_display = ['title', 'price', 'inventory_status', 'collection']
    list_editable = ['price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    ordering = ['title']
    list_per_page = 10

    
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Stable'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        update_inventory = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_inventory} products were sucesfully updated',
            messages.SUCCESS
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'order_number']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='order_number')
    def order_number(self, customer):
        url = (
            reverse('admin:warehouse_order_changelist') 
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))

        return format_html(
            '<a href="{}">{}</a>'
            ,url 
            ,customer.order_number)
        
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_number=Count('order')
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['placed_at', 'payment_status', 'customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_editable = ['payment_status']
    ordering = ['placed_at']
    list_select_related = ['customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:warehouse_product_changelist') 
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>',url,  collection.products_count)


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )