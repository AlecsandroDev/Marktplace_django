from django.contrib import admin
from .models import (
    Estado, Municipio, Cep, Perfil, Categoria, 
    Anuncio, Pedido, AnuncioPedido, Reporte, Foto, 
    Avaliacao, ItemListaDesejos
)

# Você pode customizar a exibição de cada modelo no admin criando classes ModelAdmin

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf')
    search_fields = ('nome', 'uf')

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    list_filter = ('estado',)
    search_fields = ('nome',)

@admin.register(Cep)
class CepAdmin(admin.ModelAdmin):
    list_display = ('cep', 'rua', 'bairro', 'municipio')
    search_fields = ('cep', 'rua', 'bairro')
    list_filter = ('municipio__estado',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'telefone', 'cpf', 'curso', 'ra', 'cep')
    list_filter = ('tipo', 'cep__municipio__estado')
    search_fields = ('user__username', 'user__email', 'telefone', 'cpf', 'ra')
    raw_id_fields = ('user', 'cep') # Melhora a performance para ForeignKeys com muitos itens

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_exibicao', 'slug', 'icone')
    search_fields = ('nome_exibicao', 'slug')
    prepopulated_fields = {'slug': ('nome_exibicao',)} # Ajuda a preencher o slug

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'categoria', 'valor_unitario', 'estoque', 'data_criacao')
    list_filter = ('categoria', 'data_criacao', 'usuario__perfil__tipo')
    search_fields = ('titulo', 'descricao', 'usuario__username')
    raw_id_fields = ('usuario', 'categoria')
    date_hierarchy = 'data_criacao'

class AnuncioPedidoInline(admin.TabularInline): # Para adicionar itens de pedido dentro do PedidoAdmin
    model = AnuncioPedido
    raw_id_fields = ('anuncio',)
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'valor_total', 'data_criacao', 'status_entrega')
    list_filter = ('status_entrega', 'data_criacao', 'usuario__perfil__tipo')
    search_fields = ('id', 'usuario__username')
    raw_id_fields = ('usuario',)
    date_hierarchy = 'data_criacao'
    inlines = [AnuncioPedidoInline] # Permite editar itens do pedido na mesma página

@admin.register(AnuncioPedido) # Opcional registrar separadamente se já estiver inline
class AnuncioPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'anuncio', 'qtd', 'valor_unitario_no_momento_compra', 'subtotal')
    search_fields = ('pedido__id', 'anuncio__titulo')
    raw_id_fields = ('pedido', 'anuncio')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'anuncio', 'status', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'usuario__username', 'anuncio__titulo')
    raw_id_fields = ('usuario', 'anuncio')
    date_hierarchy = 'data_criacao'

@admin.register(Foto)
class FotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_foto_display', 'anuncio_link', 'reporte_link', 'data_upload')
    list_filter = ('data_upload',)
    search_fields = ('anuncio__titulo', 'reporte__titulo')
    raw_id_fields = ('anuncio', 'reporte')

    def get_foto_display(self, obj):
        from django.utils.html import format_html
        if obj.foto:
            return format_html('<img src="{}" width="100" />', obj.foto.url)
        return "Sem imagem"
    get_foto_display.short_description = "Prévia da Foto"

    def anuncio_link(self, obj): # Helper para linkar ao anúncio no admin
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.anuncio:
            link = reverse("admin:marketplace_anuncio_change", args=[obj.anuncio.id])
            return format_html('<a href="{}">{}</a>', link, obj.anuncio.titulo)
        return "-"
    anuncio_link.short_description = "Anúncio"

    def reporte_link(self, obj): # Helper para linkar ao reporte no admin
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.reporte:
            link = reverse("admin:marketplace_reporte_change", args=[obj.reporte.id])
            return format_html('<a href="{}">{}</a>', link, obj.reporte.titulo)
        return "-"
    reporte_link.short_description = "Reporte"


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'usuario', 'rating', 'data_criacao')
    list_filter = ('rating', 'data_criacao')
    search_fields = ('anuncio__titulo', 'usuario__username', 'comentario')
    raw_id_fields = ('anuncio', 'usuario')
    date_hierarchy = 'data_criacao'

@admin.register(ItemListaDesejos)
class ItemListaDesejosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'anuncio', 'data_adicao')
    list_filter = ('data_adicao',)
    search_fields = ('usuario__username', 'anuncio__titulo')
    raw_id_fields = ('usuario', 'anuncio')
    date_hierarchy = 'data_adicao'

# Register your models here.
