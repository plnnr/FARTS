from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required


def sign_up(request):
    if request.method == 'POST':
        # Store the data from the POST request
        form = UserCreationForm(request.POST)

        # If the form is valid (eg. user's username is unique)
        if form.is_valid():
            # Save the user into the database
            user = form.save()

            # Login the newly created user
            # user = authenticate(
            #     request,
            #     form.cleaned_data['username'],
            #     form.cleaned_data['password1']
            # )
            login(request, user)

            return redirect('accounts/dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/sign_up.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

