import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from gerenciador_estoque.models import Usuario, Produto
from django.db.models import Count, Q
from .forms import UsuarioForm, ProdutoForm, LoginForm
from django.contrib import messages


# view para ADMIN


def listar_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id=usuario_id)
        if usuario.is_admin:
            query = request.GET.get('q')
            status = request.GET.get('status')
            usuarios = Usuario.objects.defer('password').all()

            if query:
                usuarios = usuarios.filter(Q(nome__icontains=query) | Q(email__icontains=query))

            if status:
                is_active = True if status == 'ativo' else False
                usuarios = usuarios.filter(is_active=is_active)

            usuarios = usuarios.filter(is_admin=False).annotate(
                estoque_produtos=Count('produtos'))
            return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})
        else:
            messages.error(request, 'Você não tem permissão para acessar essa página.')
            return redirect('dashboard')
    else:
        return redirect('login')


def desativar_usuario(request, usuario_id):
    try:
        usuario_logado_id = request.session.get('usuario_id')
        usuario_logado = Usuario.objects.get(id=usuario_logado_id)
        if usuario_logado.is_admin:
            usuario_a_desativar = get_object_or_404(Usuario, id=usuario_id)
            usuario_a_desativar.is_active = False
            usuario_a_desativar.save()
            messages.success(request, f'Usuário {usuario_a_desativar.nome} desativado com sucesso.')
        else:
            messages.error(request, 'Você não tem permissão para desativar usuários.')
        return redirect('listar_usuarios')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuarios')


def reativar_usuario(request, usuario_id):
    try:
        usuario_logado_id = request.session.get('usuario_id')
        usuario_logado = Usuario.objects.get(id=usuario_logado_id)
        if usuario_logado.is_admin:
            usuario_a_reativar = get_object_or_404(Usuario, id=usuario_id)
            usuario_a_reativar.is_active = True
            usuario_a_reativar.save()
            messages.success(request, f'Usuário {usuario_a_reativar.nome} reativado com sucesso.')
        else:
            messages.error(request, 'Você não tem permissão para reativar usuários.')
        return redirect('listar_usuarios')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuarios')


def excluir_usuario(request, usuario_id):
    try:
        usuario_logado_id = request.session.get('usuario_id')
        usuario_logado = Usuario.objects.get(id=usuario_logado_id)
        if usuario_logado.is_admin:
            usuario_a_excluir = get_object_or_404(Usuario, id=usuario_id)
            usuario_a_excluir.delete()
            messages.success(request, 'Usuário excluído com sucesso.')
        else:
            messages.error(request, 'Você não tem permissão para excluir usuários.')
        return redirect('listar_usuarios')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuarios')


# view para USUÁRIOS ===================================================================================================

def registro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.password = hashlib.sha256(usuario.password.encode('utf-8')).hexdigest()
            usuario.save()
            return redirect('login')
        else:
            return render(request, 'usuarios/registro.html', {'form': form})
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = hashlib.sha256(form.cleaned_data['password'].encode('utf-8')).hexdigest()
            try:
                usuario = Usuario.objects.get(email=email, password=password)
                if usuario is not None:
                        request.session['usuario_id'] = usuario.id
                        return redirect('dashboard')
            except Usuario.DoesNotExist:
                form.add_error(None, 'Email ou senha incorretos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


def dashboard(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        query = request.GET.get('q')
        usuario = Usuario.objects.defer('password').get(id=usuario_id)
        if usuario.is_admin:
            total_usuarios = Usuario.objects.filter(is_admin=False).count()
            usuarios_ativos = Usuario.objects.filter(is_admin=False).count()
            usuarios_inativos = total_usuarios - usuarios_ativos
            ultimos_usuarios = Usuario.objects.filter(is_admin=False)

            '''context = {
                'usuario': usuario,
                'total_usuarios': total_usuarios,
                'usuarios_ativos': usuarios_ativos,
                'usuarios_inativos': usuarios_inativos,
                'ultimos_usuarios': ultimos_usuarios
            }'''
            return render(request, 'produtos/dashboard.html', {'usuario': usuario,
                                                               'total_usuarios': total_usuarios,
                                                               'usuarios_ativos': usuarios_ativos,
                                                               'usuarios_inativos': usuarios_inativos,
                                                               'ultimos_usuarios': ultimos_usuarios})

        else:
            quantidade = request.GET.get('quantidade')
            produtos = Produto.objects.filter(usuario=usuario)
            if query:
                produtos = produtos.filter(
                    Q(nome__icontains=query) |
                    Q(descricao__icontains=query) |
                    Q(preco__icontains=query)
                )

            if quantidade:
                produtos = produtos.filter(Q(quantidade=quantidade))

            '''context = {
                'usuario': usuario,
                'produtos': produtos
            }'''
            return render(request, 'produtos/dashboard.html', {'usuario': usuario, 'produtos': produtos})
    else:
        return redirect('login')


def adicionar_produto(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        if request.method == 'POST':
            form = ProdutoForm(request.POST, request.FILES)
            if form.is_valid():
                produto = form.save(commit=False)
                produto.usuario_id = request.session.get('usuario_id')
                produto.save()
                messages.success(request, f'produto \'{produto.nome}\' adicionado com sucesso!')
                return redirect('dashboard')
            else:
                return render(request, 'produtos/adicionar_produto.html', {'form': form})
        else:
            form = ProdutoForm()
        return render(request, 'produtos/adicionar_produto.html', {'form': form})
    else:
        return redirect('login')


def editar_produto(request, produto_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        produto = get_object_or_404(Produto, id=produto_id, usuario_id=usuario_id)
        if request.method == 'POST':
            form = ProdutoForm(request.POST, request.FILES, instance=produto)
            if form.is_valid():
                produto = form.save(commit=False)
                produto.usuario_id = request.session.get('usuario_id')
                produto.save()
            form.save()
            messages.success(request, f'Produto \'{produto.nome}\' atualizado com sucesso!')
            return redirect('dashboard')
        form = ProdutoForm(instance=produto)
        return render(request, 'produtos/editar_produto.html', {'form': form, 'produto': produto})
    else:
        return redirect('login')


def excluir_produto(request, produto_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        produto = get_object_or_404(Produto, id=produto_id, usuario_id=usuario_id)
        if request.method == 'POST':
            produto.delete()
            messages.success(request, f'Produto removido com sucesso!')
            return redirect('dashboard')
        return render(request, 'produtos/remover_produto.html', {'produto': produto})
    else:
        return redirect('login')


def logout(request):
    request.session.flush()
    return redirect('login')




