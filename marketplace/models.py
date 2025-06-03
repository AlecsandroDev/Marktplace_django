from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Estado(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Estado")
    uf = models.CharField(max_length=2, unique=True, verbose_name="UF")

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.uf})"


class Municipio(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Município")
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, verbose_name="Estado")

    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.estado.uf}"


class Cep(models.Model):
    cep = models.CharField(max_length=9, verbose_name="CEP", help_text="Formato: XXXXX-XXX ou XXXXXXXX") # Aumentado para 9 para incluir hífen
    rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, verbose_name="Município")

    class Meta:
        verbose_name = "CEP"
        verbose_name_plural = "CEPs"
        ordering = ['cep']

    def __str__(self):
        return f"{self.cep} - {self.rua}, {self.numero}"


# --- Modelo de Perfil de Usuário (Extensão do User do Django) ---
class Perfil(models.Model):
    TIPOS_USUARIO = [
        ('comprador', 'Comprador'),
        ('vendedor', 'Vendedor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário", related_name="perfil")
    tipo = models.CharField(max_length=10, choices=TIPOS_USUARIO, verbose_name="Tipo de Usuário")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True, verbose_name="Foto de Perfil")
    cep = models.ForeignKey(Cep, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="CEP")
    idade = models.PositiveIntegerField(null=True, blank=True, verbose_name="Idade")
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF", help_text="Formato: XXX.XXX.XXX-XX ou XXXXXXXXXXX")
    curso = models.CharField(max_length=100, blank=True, null=True, verbose_name="Curso")
    ra = models.CharField(max_length=20, blank=True, null=True, verbose_name="RA (Registro Acadêmico)")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Categoria(models.Model):
    nome_exibicao = models.CharField(max_length=100, verbose_name="Nome de Exibição")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug", help_text="Identificador único para URLs, gerado automaticamente se deixado em branco.")
    icone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ícone", help_text="Emoji ou classe de ícone CSS (ex: 'fas fa-shopping-bag')")
    # Você pode adicionar uma imagem para a categoria se desejar:
    # imagem_categoria = models.ImageField(upload_to='categorias/', blank=True, null=True, verbose_name="Imagem da Categoria")

    class Meta:
        verbose_name = "Categoria de Anúncio"
        verbose_name_plural = "Categorias de Anúncios"
        ordering = ['nome_exibicao']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome_exibicao)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_exibicao

class Anuncio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Vendedor", related_name="anuncios") # Alterado para User do Django
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria", related_name="anuncios")
    titulo = models.CharField(max_length=255, verbose_name="Título do Anúncio")
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    imagem_principal = models.ImageField(upload_to='anuncios_principais/', blank=True, null=True, verbose_name="Imagem Principal do Anúncio")
    estoque = models.PositiveIntegerField(verbose_name="Quantidade em Estoque")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário (R$)")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    # Adicionar um campo de status se necessário (ex: 'ativo', 'pausado', 'vendido')
    # STATUS_ANUNCIO = [('ativo', 'Ativo'), ('pausado', 'Pausado'), ('vendido', 'Vendido')]
    # status = models.CharField(max_length=10, choices=STATUS_ANUNCIO, default='ativo', verbose_name="Status")

    class Meta:
        verbose_name = "Anúncio"
        verbose_name_plural = "Anúncios"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    STATUS_ENTREGA_CHOICES = [
        ('pendente', 'Pendente de Pagamento'),
        ('processando', 'Em Processamento'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Comprador", related_name="pedidos") # Alterado para User do Django
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total (R$)")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")
    status_entrega = models.CharField(max_length=20, choices=STATUS_ENTREGA_CHOICES, default='pendente', verbose_name="Status da Entrega")
    # Adicionar campos de endereço de entrega se não for sempre o CEP do perfil do usuário

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.nome}"

class AnuncioPedido(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, verbose_name="Anúncio")
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, verbose_name="Pedido", related_name="itens")
    qtd = models.PositiveIntegerField(verbose_name="Quantidade Comprada")
    valor_unitario_no_momento_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário (na compra)", help_text="Registra o preço do anúncio no momento da compra.")

    class Meta:
        unique_together = (('anuncio', 'pedido'),)
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Itens de Pedidos"

    def save(self, *args, **kwargs):
        if not self.valor_unitario_no_momento_compra:
            self.valor_unitario_no_momento_compra = self.anuncio.valor_unitario
        super().save(*args, **kwargs)
        
    @property
    def subtotal(self):
        return self.qtd * self.valor_unitario_no_momento_compra
    
    def __str__(self):
        return f"{self.qtd}x {self.anuncio.titulo} no Pedido {self.pedido.id}"

class Reporte(models.Model):
    STATUS_REPORTE_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_analise', 'Em Análise'),
        ('resolvido', 'Resolvido'),
        ('arquivado', 'Arquivado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário Reportante", related_name="reportes_feitos") # Alterado para User do Django
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, verbose_name="Anúncio Reportado", related_name="reportes_recebidos")
    titulo = models.CharField(max_length=255, verbose_name="Título do Reporte")
    descricao = models.TextField(verbose_name="Descrição do Reporte")
    status = models.CharField(max_length=20, choices=STATUS_REPORTE_CHOICES, default='aberto', verbose_name="Status do Reporte")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data do Reporte")

    class Meta:
        unique_together = (('usuario', 'anuncio'),) # Um usuário só pode reportar um anúncio uma vez.
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Reporte de {self.usuario.username} sobre {self.anuncio.titulo}"


class Foto(models.Model):
    foto = models.ImageField(upload_to='fotos_uploads/', verbose_name="Arquivo da Foto") # Alterado upload_to
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Reporte Associado", related_name="fotos")
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Anúncio Associado", related_name="fotos_adicionais")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"
        ordering = ['-data_upload']

    def clean(self):
        if not (self.reporte or self.anuncio):
            raise ValidationError('A foto deve estar vinculada a um Reporte OU a um Anúncio.')
        if self.reporte and self.anuncio:
            raise ValidationError('A foto não pode estar vinculada a um Reporte E a um Anúncio simultaneamente.')

    def __str__(self):
        if self.reporte:
            return f"Foto do Reporte ID {self.reporte.id}"
        elif self.anuncio:
            return f"Foto do Anúncio '{self.anuncio.titulo}'"
        return "Foto desvinculada" # Não deveria ocorrer se 'clean' for respeitado

class Avaliacao(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Anúncio Avaliado")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas', verbose_name="Usuário Avaliador")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nota (1-5)"
    )
    comentario = models.TextField(verbose_name="Comentário")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Avaliação")

    class Meta:
        unique_together = (('anuncio', 'usuario'),) # Um usuário só pode avaliar um anúncio uma vez.
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Avaliação de {self.usuario.username} para '{self.anuncio.titulo}' - Nota: {self.rating}"


class ItemListaDesejos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lista_desejos_itens', verbose_name="Usuário")
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='desejado_por_usuarios', verbose_name="Anúncio")
    data_adicao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Adição")

    class Meta:
        unique_together = (('usuario', 'anuncio'),)
        verbose_name = "Item da Lista de Desejos"
        verbose_name_plural = "Itens da Lista de Desejos"
        ordering = ['-data_adicao']

    def __str__(self):
        return f"'{self.anuncio.titulo}' na lista de desejos de {self.usuario.username}"