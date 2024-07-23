import hashlib
from django import forms
from gerenciador_estoque.models import Usuario, Produto


class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UsuarioForm(BootStrapModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }


class ProdutoForm(BootStrapModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'quantidade']

        widgets = {
            'preco': forms.TextInput(attrs={'data-mask': '00.000.000,00', 'data-mask-reverse': 'true'}),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control my-2', 'placeholder': 'Digite seu email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Digite sua senha'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                usuario = Usuario.objects.get(email=email)
                hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                if usuario.password != hashed_password:
                    raise forms.ValidationError('Email ou senha inválidos')
            except Usuario.DoesNotExist:
                raise forms.ValidationError('Email não encontrado')
        return cleaned_data


