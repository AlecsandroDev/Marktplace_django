from django.contrib import admin
from .models import (
    Estado, Municipio, Cep, Perfil, Categoria, 
    Anuncio, Pedido, AnuncioPedido, Reporte, Foto, 
    Avaliacao, ItemListaDesejos
)

admin.site.register(Estado)
admin.site.register(Municipio)
admin.site.register(Cep)
admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(Anuncio)
admin.site.register(Pedido)
admin.site.register(AnuncioPedido)
admin.site.register(Reporte)
admin.site.register(Foto)
admin.site.register(Avaliacao)
admin.site.register(ItemListaDesejos)
# Register your models here.
