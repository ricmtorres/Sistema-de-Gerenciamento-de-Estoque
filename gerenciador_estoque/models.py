from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'usuarios'
        db_table = 'usuario'
        verbose_name = 'usuario'
        ordering = ['-created_at']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    preco = models.CharField(blank=True, max_length=50)
    quantidade = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'
        db_table = 'produto'
        ordering = ['nome']

    def __str__(self):
        return self.nome