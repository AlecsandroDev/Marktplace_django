from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciais inválidas ou você não tem permissão para acessar o admin.')
            return redirect('login')

    return render(request, "admin/login.html")


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_anuncios(request):
    return render(request, "admin/anuncios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios(request):
    return render(request, "admin/usuarios.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_usuario(request):
    return render(request, "admin/gerenciar_usuario.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes(request):
    return render(request, "admin/reportes.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte(request):
    return render(request, "admin/gerenciar_reporte.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportes_arquivados(request):
    return render(request, "admin/reportes_arquivados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_reporte_arquivado(request):
    return render(request, "admin/gerenciar_reporte_arquivado.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos(request):
    return render(request, "admin/pedidos.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido(request):
    return render(request, "admin/gerenciar_pedido.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_pedidos_finalizados(request):
    return render(request, "admin/pedidos_finalizados.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_gerenciar_pedido_finalizado(request):
    return render(request, "admin/gerenciar_pedido_finalizado.html")

@login_required
def admin_logout(request):
    logout(request)
    return redirect('login')
