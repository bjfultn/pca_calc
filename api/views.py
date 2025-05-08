import os
import time as ostime
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from db.models import Car
from pca_calc.class_table import class_table
from django.core.management import call_command
from django.conf import settings
import tempfile


@login_required
def competition(request):
    start_time = ostime.time()
    
    # Fetch all cars with related data in a single query
    cars = Car.objects.select_related('user').prefetch_related(
        'tires', 'upgrades'
    ).all()
    print(f"Database query took {ostime.time() - start_time:.4f} seconds", flush=True)
    
    # Process the cars
    process_start = ostime.time()
    car_list = []
    
    # Track total time for each calculation type
    base_time = 0
    tire_time = 0
    upgrade_time = 0
    total_time = 0
    dict_time = 0
    class_time = 0
    
    # Pre-calculate total points for all cars
    for car in cars:
        if car.upgrades.exists() and car.tires.exists():
            # Time each point calculation
            base_start = ostime.time()
            base_points = car.base_points()
            base_time += ostime.time() - base_start
            
            tire_start = ostime.time()
            tire_points = car.tires.last().tire_points()
            tire_time += ostime.time() - tire_start
            
            upgrade_start = ostime.time()
            upgrade_points = car.upgrades.last().upgrade_points()
            upgrade_time += ostime.time() - upgrade_start
            
            total_start = ostime.time()
            total_points = base_points + tire_points + upgrade_points
            total_time += ostime.time() - total_start
            
            # Find class using binary search
            class_start = ostime.time()
            class_name = ''
            left = 0
            right = len(class_table) - 1
            class_ranges = list(class_table.values())
            class_names = list(class_table.keys())
            
            while left <= right:
                mid = (left + right) // 2
                if class_ranges[mid][0] < total_points <= class_ranges[mid][1]:
                    class_name = class_names[mid]
                    break
                elif total_points <= class_ranges[mid][0]:
                    right = mid - 1
                else:
                    left = mid + 1
            class_time += ostime.time() - class_start
            
            dict_start = ostime.time()
            car_list.append({
                'id': car.id,
                'user_name': f"{car.user.first_name} {car.user.last_name}",
                'year': car.year,
                'make': car.make,
                'model': car.model,
                'base_points': base_points,
                'tire_points': tire_points,
                'upgrade_points': upgrade_points,
                'total_points': total_points,
                'class': class_name
            })
            dict_time += ostime.time() - dict_start
    
    print(f"Base points total time: {base_time:.4f} seconds", flush=True)
    print(f"Tire points total time: {tire_time:.4f} seconds", flush=True)
    print(f"Upgrade points total time: {upgrade_time:.4f} seconds", flush=True)
    print(f"Total points calculation time: {total_time:.4f} seconds", flush=True)
    print(f"Class name calculation time: {class_time:.4f} seconds", flush=True)
    print(f"Dictionary creation time: {dict_time:.4f} seconds", flush=True)
    print(f"Processing cars took {ostime.time() - process_start:.4f} seconds", flush=True)
    
    print(f"Total execution time: {ostime.time() - start_time:.4f} seconds", flush=True)
    return JsonResponse(car_list, safe=False)


@login_required
def user_settings(request, key=None):
    """URL to save and fetch user settings
    Currently these functions only work with the Candidates table
    """
    # Fetch a setting from user data with default of None
    if key and request.method == "GET":
        default_value = None

        # Return a stored setting or default value
        data = request.user.data.get(key, default_value)
        return JsonResponse(data)

    return HttpResponse(status=404)


@login_required
def database_backup(request):
    if not request.user.is_superuser:
        return HttpResponse(status=404)
    else:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            # Run dumpdata command
            call_command(
                'dumpdata',
                '--exclude', 'auth.permission',
                '--exclude', 'contenttypes',
                '--exclude', 'sessions.session',
                '--exclude', 'users.user',
                stdout=temp_file
            )
            temp_file.flush()
            
            # Create the response
            response = FileResponse(
                open(temp_file.name, 'rb'),
                as_attachment=True,
                filename='db_backup.json'
            )
            
            # Clean up the temporary file after sending
            os.unlink(temp_file.name)
            
            return response
