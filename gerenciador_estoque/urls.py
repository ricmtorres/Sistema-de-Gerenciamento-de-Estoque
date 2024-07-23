from django.urls import path
from . import views

urlpatterns = [
    path('registro', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('produto/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produto/editar/<int:produto_id>', views.editar_produto, name='editar_produto'),
    path('produto/excluir/<int:produto_id>', views.excluir_produto, name='excluir_produto'),
    path('logout', views.logout, name='logout'),
    path('admin/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('admin/desativar/<int:usuario_id>', views.desativar_usuario, name='desativar_usuario'),
    path('admin/reativar/<int:usuario_id>', views.reativar_usuario, name='reativar_usuario'),
    path('admin/excluir/<int:usuario_id>', views.excluir_usuario, name='excluir_usuario'),
]
