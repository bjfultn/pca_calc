from db.models.car import Car, CarCreateForm
from db.models.tire import Tire, TireCreateForm
from db.models.upgrades import Upgrades, UpgradesCreateForm
from glob import glob

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'pages/home.haml', {})

@login_required
def garage(request):
    user = request.user
    cars = user.cars.all()

    return render(request, 'pages/garage.haml', {'cars': cars})

@login_required
def competition(request):
    cars = Car.objects.all()
    return render(request, 'pages/competition.haml', {'cars': cars})

@login_required
def add_car(request):
    if request.method == 'POST':
        form = CarCreateForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()

            tire = Tire.objects.create(car=car)
            tire.save()

            upgrades = Upgrades.objects.create(car=car)
            upgrades.save()

            return redirect('/garage/')
        else:
            return render(request, 'pages/form.haml', {'form': form, 'mode': 'add'})

    else:        
        form = CarCreateForm()
        car = None

    return render(request, 'pages/form.haml', {'form': form, 'mode': 'add',
                                               'car': car})

@login_required
def edit_car(request, carid):
    car = Car.objects.filter(user=request.user).get(id=carid)
    if request.method == 'POST':
        form = CarCreateForm(request.POST, request.FILES, instance=car)
        car = form.save()

        return redirect('/garage/')
    else:        
        form = CarCreateForm(instance=car)

    return render(request, 'pages/form.haml', {'form': form, 'mode': 'edit', 
                                                'carid': carid,
                                                'car': car})    

@login_required
def delete_car(request, carid):
    car = Car.objects.filter(user=request.user).get(id=carid)
    car.delete()

    return redirect('/garage/')

@login_required
def edit_tire(request, carid):
    car = Car.objects.filter(user=request.user).get(id=carid)
    tires = car.tires.last()
    if request.method == 'POST':
        form = TireCreateForm(request.POST, request.FILES, instance=tires)
        tires = form.save()

        return redirect(request.path)
    else:        
        form = TireCreateForm(instance=tires)

    return render(request, 'pages/form.haml', {'form': form, 'mode': 'edit', 
                                                'carid': carid,
                                                'car': car})

@login_required
def edit_upgrades(request, carid):
    car = Car.objects.filter(user=request.user).get(id=carid)
    upgrades = car.upgrades.all().last()
    if request.method == 'POST':
        form = UpgradesCreateForm(request.POST, request.FILES, instance=upgrades)
        upgrades = form.save()

        return redirect(request.path)
    else:        
        form = UpgradesCreateForm(instance=upgrades)

    return render(request, 'pages/form.haml', {'form': form, 'mode': 'edit', 
                                                'carid': carid,
                                                'car': car})


@login_required
def view_car(request, carid):
    car = Car.objects.get(id=carid)
    tires = car.tires.all().last()
    upgrades = car.upgrades.all().last()
    
    return render(request, 'pages/car.haml', {'car': car})
