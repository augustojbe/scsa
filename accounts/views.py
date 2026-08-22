from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import SignupForm
from base.mixins import BrokerageRequiredMixin


class LandingView(TemplateView):
    template_name = 'accounts/landing.html'


class HomeView(BrokerageRequiredMixin, TemplateView):
    template_name = 'accounts/home.html'


class SignupView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            form.save()
        messages.success(
            self.request,
            'Conta criada com sucesso! Entre com seu e-mail e senha.',
        )
        return super().form_valid(form)
