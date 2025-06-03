from django.db import models

class Estado(models.Model):
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.nome} ({self.uf})"


class Municipio(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.estado.uf}"


class Cep(models.Model):
    cep = models.CharField(max_length=8)
    rua = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cep} - {self.rua}, {self.numero}"


class Usuario(models.Model):
    TIPOS = [
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    ]

    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)  # Melhor aumentar para segurança
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_cadastro = models.DateField(auto_now_add=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cep = models.ForeignKey(Cep, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    estoque = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(auto_now_add=True)
    status_entrega = models.CharField(max_length=20)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.nome}"


class AnuncioPedido(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    qtd = models.IntegerField()

    class Meta:
        unique_together = (('anuncio', 'pedido'),)

    def __str__(self):
        return f"{self.qtd}x {self.anuncio.titulo} no Pedido {self.pedido.id}"


class Reporte(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    status = models.CharField(max_length=20)
    data = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (('usuario', 'anuncio'),)

    def __str__(self):
        return f"Reporte de {self.usuario.nome} sobre {self.anuncio.titulo}"


class Foto(models.Model):
    foto = models.ImageField(upload_to='fotos/')
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, blank=True, null=True)
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.reporte is None and self.anuncio is None) or (self.reporte is not None and self.anuncio is not None):
            raise ValidationError('A foto deve estar vinculada a um Reporte OU a um Anuncio, não ambos.')

    def __str__(self):
        if self.reporte:
            return f"Foto de Reporte {self.reporte}"
        elif self.anuncio:
            return f"Foto de Anuncio {self.anuncio.titulo}"
        else:
            return "Foto sem vínculo"
# Create your models here.
