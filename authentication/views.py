

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import HeadOffice, Client,Branches
from asset_App.models import Asset_movement_data,AssetData
from django.contrib import messages
from .forms import LoginForm, MasterAdminCreationForm, SuperAdminCreationForm, AdminCreationForm, HeadOfficeForm, ClientForm,BranchForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from .models import Client, HeadOffice, Branches
from asset_App.models import Depreciation,Asset_movement_data,AssetData



from django.utils import timezone
def masterAdminDashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')

    client = Client.objects.count()
    head_office_count = HeadOffice.objects.count()
    branch_count = Branches.objects.count()

    # Get overall assets by type
    overall_assets = AssetData.objects.values('asset_type__name').annotate(count=Count('id'))

    # Get asset status
    asset_status = {
        'Shifted': Asset_movement_data.objects.filter(status='permanent').count(),
        'Pending': Asset_movement_data.objects.filter(status='temporary').count(),
        'Available': AssetData.objects.count() - Asset_movement_data.objects.count(),
        'Sold': AssetData.objects.filter(is_sold=True).count()  # Adjust this if needed
    }

    # Get warranty checks (assuming you have a field for warranty expiry)
    warranty_checks = AssetData.objects.filter(
        warranty_info__isnull=False
    ).order_by('warranty_info')[:5]  # Get top 5 upcoming warranty expirations

    # Get depreciation details
    depreciation_data = {}
    all_depreciations = Depreciation.objects.select_related('asset')  # Join with AssetData

    for depreciation in all_depreciations:
        asset_name = depreciation.asset.asset_type  # or another relevant field
        calculated_depreciation = depreciation.calculate_depreciation()  # Assuming this method returns a list of tuples (year, value)

        for year, value in calculated_depreciation:
            if asset_name not in depreciation_data:
                depreciation_data[asset_name] = 0
            depreciation_data[asset_name] += value  # Summing up depreciation values

    # Prepare data for the chart
    asset_depreciation = [
        [asset, value] for asset, value in depreciation_data.items()
    ]
    
    
    
    asset_movements = Asset_movement_data.objects.values(
        'from_branch__branch_name',  # Ensure this field exists in the Branches model
        'to_branch__branch_name',    # Ensure this field exists in the Branches model
        'asset__asset_name'
    ).annotate(count=Count('id'))
    
    # Get asset movements
    movement_data = []
    for movement in asset_movements:
        movement_data.append([movement['from_branch__branch_name'], movement['to_branch__branch_name'], movement['count']])
    
    # Get total assets collected by each branch
    branch_collection = Branches.objects.annotate(
        total_received=Sum('movements_to__asset__id')  # Count assets moved to this branch
    ).order_by('-total_received')  # Order branches by total collected assets

    # Get total movements for today
    today = timezone.now().date()
    shifts_today_count = Asset_movement_data.objects.filter(movement_date=today).count()


    context = {
        'client': client,
        'head_office_count': head_office_count,
        'branch_count': branch_count,
        'overall_assets': overall_assets,
        'asset_status': asset_status,
        'warranty_checks': warranty_checks,
        'depreciation_data': asset_depreciation,
         
        'asset_movements': movement_data,  # Pass the prepared movement data for Sankey chart
        'branch_collection': branch_collection,  # Pass branch collection data
        'shifts_today_count': shifts_today_count,# Pass the prepared movement data for Sankey chart
    }

    return render(request, 'authentication/master_dashboard.html', context)





# def superAdminDashboard(request):
#     if not request.user.is_authenticated or not request.user.is_superadmin:
#         return redirect('login')
    
#     user = request.user
#     head_office = user.head_office
    
#     if head_office:
#         branches = Branches.objects.filter(head_office=head_office)
#         assets = AssetData.objects.filter(branch__in=branches)
#         asset_shifted_count = Asset_movement_data.objects.filter(from_branch__in=branches).count()

#         context = {
#             'head_office': head_office,
#             'branches': branches,
#             'assets': assets,
#             'asset_shifted_count': asset_shifted_count,
#         }
#         return render(request, 'authentication/super_dashboard.html', context)
#     else:
#         messages.error(request, "No head office assigned to this superadmin.")
#         return redirect('login')    


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Sum, Case, When, Value, CharField


def get_new_arrivals():
    # Calculate the date 7 days ago
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    
    # Query for assets purchased in the last 7 days
    new_arrivals = AssetData.objects.filter(
        purchase_date__gte=seven_days_ago
    ).select_related('asset_type').order_by('-purchase_date')
    
    # You can limit the number of results if needed
    # new_arrivals = new_arrivals[:10]  # Uncomment to limit to 10 results
    
    return new_arrivals

from datetime import datetime, timedelta
from django.db.models import F, ExpressionWrapper, DurationField, DateTimeField
def superAdminDashboard(request):
    

    user = request.user
    head_office = user.head_office

    if head_office:
        branches = Branches.objects.filter(head_office=head_office)
        assets = AssetData.objects.filter(branch__in=branches)
        department=Departments.objects.all()
        
        # Get asset counts and values
        total_assets = assets.filter(is_sold=False).count()
        sold_assets = assets.filter(is_sold=True).count()  # Assuming "status" is the field tracking sold assets
        total_branches = branches.count()
        
        # Get asset movements (shifted assets)
        asset_movements = Asset_movement_data.objects.filter(from_branch__in=branches)
        shifted_assets = asset_movements.count()

        # Get asset counts by category (for the graph)
        asset_categories = assets.values('asset_type__name').annotate(count=Count('id'))

        # Get asset status counts (for the graph)
        asset_status = assets.values('is_sold').annotate(count=Count('id')).annotate(
            status=Case(
                When(is_sold=True, then=Value('Sold')),
                default=Value('Available'),
                output_field=CharField(),
            )
        )
        
        one_week_ago = timezone.now() - timedelta(days=7)
        new_arrivals = assets.filter(purchase_date__gte=one_week_ago).order_by('-purchase_date')[:5]

        # Get recent asset movements
        recent_movements = asset_movements.order_by('-movement_date')[:5]
        today = datetime.now().date()
        warranty_threshold = today + timedelta(days=90)
        
        warranty_expiring_assets = AssetData.objects.filter(
            warranty_info__isnull=False,
            is_sold=False
        ).annotate(
            warranty_end_date=ExpressionWrapper(
                F('purchase_date') + timedelta(days=365),  # Assuming 1-year warranty
                output_field=DateTimeField()
            ),
            warranty_days_left=ExpressionWrapper(
                F('warranty_end_date') - today,
                output_field=DurationField()
            )
        ).filter(
            warranty_end_date__lte=warranty_threshold
        ).order_by('warranty_days_left')
        
        dpt_asset = AssetData.objects.filter(
        branch__in=branches
    ).values('department__dpt_name').annotate(
        count=Count('id')
    )

        context = {
            'head_office': head_office,
            'total_assets': total_assets,
            'sold_assets': sold_assets,
            'total_branches': total_branches,
            'shifted_assets': shifted_assets,
            'asset_categories': asset_categories,
            'asset_status': asset_status,
            'recent_movements': recent_movements,
            'new_arrivals': new_arrivals,
            'warranty_expiring_assets': warranty_expiring_assets,
            'warranty_expiring_count': warranty_expiring_assets.count(),
            'dpt_asset': dpt_asset
        }
        return render(request, 'authentication/super_dashboard.html', context)
    else:
        messages.error(request, "No head office assigned to this superadmin.")
        return redirect('login')
    
from django.db.models import Q
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from asset_App.models import AssetData, Asset_movement_data, Depreciation





def AdminDashboard(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('login')

    user = request.user
    if user.is_admin and user.branch:
        branch = user.branch
        # Filter assets by branch
        assets = AssetData.objects.filter(branch=branch)

        # Get asset counts and values for the branch
        total_assets = assets.filter(is_sold=False).count()
        total_asset_value = assets.aggregate(Sum('price'))['price__sum'] or 0
        sold_assets_count = assets.filter(is_sold=True).count()

        # Get asset movements for the branch
        asset_shifted_count = Asset_movement_data.objects.filter(
            Q(from_branch=branch) | Q(to_branch=branch)
        ).count()

        # Filter for new arrivals within the last 7 days, excluding sold assets
        new_arrivals = assets.filter(
            purchase_date__gte=timezone.now() - timezone.timedelta(days=7),
            is_sold=False  # Exclude sold assets
        )

        # Get asset categories count
        asset_categories = assets.values('asset_type__name').annotate(count=Count('id'))

        # Get depreciation data
        depreciations = Depreciation.objects.filter(asset__in=assets)
        total_depreciation = depreciations.aggregate(Sum('purchase_value'))['purchase_value__sum'] or 0

        # Get recent asset movements (limit to last 5)
        recent_movements = Asset_movement_data.objects.filter(
            Q(from_branch=branch) | Q(to_branch=branch)
        ).order_by('-movement_date')[:5]

        # Get asset status
        asset_status = assets.values('is_sold').annotate(count=Count('id')).annotate(
            status=Case(
                When(is_sold=True, then=Value('Sold')),
                default=Value('Available'),
                output_field=CharField(),
            )
        )

        # Context data to pass to template
        context = {
            'branch': branch,
            'total_assets': total_assets,
            'total_asset_value': total_asset_value,
            'sold_assets_count': sold_assets_count,
            'asset_shifted_count': asset_shifted_count,
            'new_arrivals': new_arrivals,
            'asset_categories': asset_categories,
            'total_depreciation': total_depreciation,
            'recent_movements': recent_movements,
            'asset_status': asset_status,
        }
        return render(request, 'authentication/admin_dashboard.html', context)
    else:
        messages.error(request, "No branch assigned to this admin.")
        return redirect('login')

def Home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'authentication/home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.is_superuser:
                    return redirect('master_admin_dashboard')
                elif user.is_superadmin:
                    return redirect('super_admin_dashboard')
                elif user.is_admin:
                    return redirect('branch_dashboard')
                else:
                    return redirect('home')  # General home page or dashboard
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})




from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.http import HttpResponseRedirect

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view_for_asset(request, asset_id=None):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if asset_id:
                    return redirect('asset_link', asset_id=asset_id)
                return redirect('home')  # or whatever your default redirect should be
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login_view_for_asset.html', {
        'form': form,
        'asset_id': asset_id
    })
    



def logout_view(request):
    logout(request)
    return redirect('login')

from .models import CustomUser

def create_super_admin(request):
    if request.method == 'POST':
        form = SuperAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not user.head_office:
                messages.error(request, "Please assign a head office to the superadmin.")
                return render(request, 'authentication/create_super_admin.html', {'form': form})
            login(request, user)
            return redirect('super_admin_dashboard')
    else:
        form = SuperAdminCreationForm()
    return render(request, 'authentication/create_super_admin.html', {'form': form})
# def create_super_admin(request):
#     if request.method == 'POST':
#         form = SuperAdminCreationForm(request.POST)
#         if form.is_valid():
#             head_office = form.cleaned_data['head_office']
            
            

#             user = form.save()  # Save the user with the is_superadmin=True
#             login(request, user)
#             return redirect('super_admin_dashboard')
#     else:
#         form = SuperAdminCreationForm()

#     return render(request, 'authentication/create_super_admin.html', {'form': form})

def dashboard_view(request):
    context = {
        'user_role': request.user.role if hasattr(request.user, 'role') else None,
        'head_office': HeadOffice.objects.filter(user=request.user).first(),
        'branch': Branches.objects.filter(user=request.user).first(),
    }
    return render(request, 'authentication/dashboard.html', context)



def create_admin(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save()
            user.is_branch=True
            if not user.branch:
                messages.error(request, "Please assign a branch to the admin.")
                return render(request, 'authentication/create_admin.html', {'form': form})
            login(request, user)
            return redirect('branch_dashboard')
    else:
        form = AdminCreationForm()
    return render(request, 'authentication/create_admin.html', {'form': form})

def create_master_admin(request):
   
    if request.method == 'POST':
        form = MasterAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'{user} Logged in Successfully')
            return redirect('master_admin_dashboard')  # Redirect to master admin dashboard
    else:
        form = MasterAdminCreationForm()
    return render(request, 'authentication/create_master_admin.html', {'form': form})





def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            client = form.save(commit=False)
            is_head_office = form.cleaned_data['is_head_office']
            is_branch = form.cleaned_data['is_branch']

            client.save()

            if is_head_office:
                head_office = HeadOffice.objects.create(
                    prefix=client.prefix, 
                    client=client, 
                    name=client.client_name, 
                    address=client.client_address, 
                    contact_number=client.client_contact,
                    logo_image=client.logo_image
                )

            if is_branch:
                if is_head_office:
                    Branches.objects.create(
                        prefix=client.prefix, 
                        head_office=head_office, 
                        branch_name=client.client_name, 
                        branch_address=client.client_address, 
                        branch_contact_number=client.client_contact,
                        logo_image=client.logo_image
                    )
                else:
                    Branches.objects.create(
                        prefix=client.prefix, 
                        head_office=None, 
                        branch_name=client.client_name, 
                        branch_address=client.client_address, 
                        branch_contact_number=client.client_contact,
                        logo_image=client.logo_image
                    )

            messages.success(request, 'Client created successfully')
            return redirect('master_admin_dashboard')
        else:
            messages.error(request, 'Creating client error occurred')
    else:
        form = ClientForm()
    return render(request, 'authentication/client.html', {'form': form})


def edit_client(request, pk):
    
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form = ClientForm(request.POST,request.FILES, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            is_head_office = form.cleaned_data['is_head_office']
            is_branch = form.cleaned_data['is_branch']

            client.save()

            head_office = HeadOffice.objects.filter(client=client).first()
            if is_head_office:
                if head_office:
                    head_office.prefix = client.prefix
                    head_office.name = client.client_name
                    head_office.address = client.client_address
                    head_office.contact_number = client.client_contact,
                    head_office.logo_image=client.logo_image
                    head_office.save()
                else:
                    head_office = HeadOffice.objects.create(
                        prefix=client.prefix,
                        client=client,
                        name=client.client_name,
                        address=client.client_address,
                        contact_number=client.client_contact,
                        logo_image=client.logo_image
                    )

            if is_branch:
                branch = Branches.objects.filter(head_office=head_office).first()
                if branch:
                    branch.prefix = client.prefix
                    branch.branch_name = client.client_name
                    branch.branch_address = client.client_address
                    branch.branch_contact_number = client.client_contact
                    branch.logo_image=client.logo_image
                    branch.save()
                else:
                    Branches.objects.create(
                        prefix=client.prefix,
                        head_office=head_office,
                        branch_name=client.client_name,
                        branch_address=client.client_address,
                        branch_contact_number=client.client_contact,
                        logo_image=client.logo_image
                    )

            messages.success(request, 'Client updated successfully')
            return redirect('master_admin_dashboard')
        else:
            messages.error(request, 'Updating client error occurred')
    else:
        form = ClientForm(instance=client)

    return render(request, 'authentication/client.html', {'form': form})



def delete_client(request, pk):
    
    client = get_object_or_404(Client, pk=pk)

    client.delete()
    messages.success(request, 'Client deleted successfully')
    return redirect('list_client')




def listofclients(request):
    list_of_clients = Client.objects.all()
    return render(request, 'authentication/list_of_clients.html', {'list_of_clients': list_of_clients})

from django.db import transaction
def addHeadofficeView(request):
    if request.method == 'POST':
        form = HeadOfficeForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            client = form.cleaned_data['client']
            existing_head_office = HeadOffice.objects.filter(client=client).first()
            
            if existing_head_office:
                messages.warning(request, 'A head office already exists for this client.')
                return redirect('list_head_office')
            
            with transaction.atomic():
                head_office = form.save(commit=False)
                is_branch = form.cleaned_data['is_branch']
                head_office.save()

            if is_branch:
                Branches.objects.create(
                    prefix=head_office.prefix,
                    head_office=head_office,
                    branch_name=head_office.name,
                    branch_address=head_office.address,
                    branch_contact_number=head_office.contact_number,
                    logo_image=head_office.logo_image
                )

            messages.success(request, 'Head Office created successfully')
            return redirect('list_head_office')
        else:
            messages.error(request, 'Creating head office error occurred')
    else:
        form = HeadOfficeForm()
    return render(request, 'authentication/headoffice.html', {'form': form})



def listofHeadoffice(request):
    # if not request.user.is_authenticated or not request.user.is_superuser or not request.user.is_superadmin:
    #     return redirect('login')
    user = request.user
    if user.is_superuser:
        head_offices = HeadOffice.objects.all()
        branches = Branches.objects.all()
    elif  user.is_superadmin and user.head_office:
        try:
            head_office = HeadOffice.objects.get(user=user)
            head_offices = HeadOffice.objects.filter(id=head_office.id)
            branches = Branches.objects.filter(head_office=head_office)
        except HeadOffice.DoesNotExist:
            head_offices = HeadOffice.objects.none()
            branches = Branches.objects.none()
    else:
        head_offices = HeadOffice.objects.none()
        branches = Branches.objects.none()

    return render(request, 'authentication/list_of_office.html', {'head_offices': head_offices, 'branches': branches})



def addBranches(request):
    if request.method == 'POST':
        form = BranchForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branches created successfully')
            return redirect('branch_list')
        else:
            messages.error(request, f'Creating Branches error occurred')
    else:
        form = BranchForm()
    return render(request, 'authentication/branches.html', {'form': form})



def listofBranches(request):
    
    user = request.user
    if user.is_superuser:
        branches = Branches.objects.all()
    elif user.is_superadmin and user.head_office:
        branches = Branches.objects.filter(head_office=user.head_office)
    else:
        branches = Branches.objects.none()
    return render(request, 'authentication/list_of_branches.html', {'branches': branches})





def editHeadOfficeView(request, id):
    head_office = get_object_or_404(HeadOffice, id=id)

    if request.method == 'POST':
        form = HeadOfficeForm(request.POST,request.FILES, instance=head_office)
        if form.is_valid():
            head_office = form.save(commit=False)
            is_branch = form.cleaned_data['is_branch']
            head_office.save()

            if is_branch:
                branch = Branches.objects.filter(head_office=head_office).first()
                if branch:
                    branch.prefix = head_office.prefix
                    branch.branch_name = head_office.name
                    branch.branch_address = head_office.address
                    branch.branch_contact_number = head_office.contact_number
                    branch.logo_image=head_office.logo_image
                    branch.save()
                else:
                    Branches.objects.create(
                        prefix=head_office.prefix,
                        head_office=head_office,
                        branch_name=head_office.name,
                        branch_address=head_office.address,
                        branch_contact_number=head_office.contact_number,
                        logo_image=head_office.logo_image
                    )
            else:
                Branches.objects.filter(head_office=head_office).delete()

            messages.success(request, 'Head Office updated successfully')
            return redirect('list_head_office')
        else:
            messages.error(request, 'Updating head office error occurred')
    else:
        form = HeadOfficeForm(instance=head_office)

    return render(request, 'authentication/headoffice.html', {'form': form})



from django.contrib import messages

def delete_head_office(request, head_office_id):
    head_office = get_object_or_404(HeadOffice, id=head_office_id)
    head_office.delete()
    messages.success(request, 'Head Office deleted successfully')
    return redirect('list_head_office')
        


def edit_branch(request, branch_id):
    branch = get_object_or_404(Branches, id=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST,request.FILES, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully')
            return redirect('branch_list')
        else:
            messages.error(request, 'Updating branch error occurred')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'authentication/edit_branch.html', {'form': form, 'branch': branch})


def delete_branch(request, branch_id):
    
    branch = get_object_or_404(Branches, id=branch_id)

    branch.delete()
    messages.success(request, 'Branch deleted successfully')
    return redirect('branch_list')



from .models import RolePermission
from .forms import RolePermissionForm
from django.http import JsonResponse


def get_user_role(user):
    if user.is_superuser:
        return 'superuser'
    elif user.groups.filter(name='Super Admin').exists():
        return 'super_admin'
    elif user.groups.filter(name='Admin').exists():
        return 'admin'
    else:
        return 'unknown'

def get_user_permissions(user):
    if user.is_superuser:
        permissions = RolePermission.objects.filter(enabled=True).values_list('permission', flat=True)
    elif user.groups.filter(name='Super Admin').exists():
        permissions = RolePermission.objects.filter(role='super_admin', enabled=True).values_list('permission', flat=True)
    elif user.groups.filter(name='Admin').exists():
        permissions = RolePermission.objects.filter(role='admin', enabled=True).values_list('permission', flat=True)
    else:
        permissions = []
    return list(permissions)



def manage_permissions(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    
    permissions = RolePermission.objects.all()
    user_permissions = get_user_permissions(request.user)

    if request.method == 'POST':
        form = RolePermissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_permissions')
    else:
        form = RolePermissionForm()

    context = {
        'form': form,
        'permissions': permissions,
        'user_permissions': user_permissions,
    }
    return render(request, 'authentication/manage_permissions.html', context)


def toggle_permission(request, permission_id):
    if request.method == 'POST':
        permission = get_object_or_404(RolePermission, id=permission_id)
        permission.enabled = not permission.enabled
        permission.save()
        return JsonResponse({'status': 'success', 'enabled': permission.enabled})
    return JsonResponse({'status': 'error'}, status=400)

def delete_permission(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser :
        return redirect('login')
    permission = get_object_or_404(RolePermission, pk=pk)
    if request.method == 'POST':
        permission.delete()
        return redirect('manage_permissions')
    return render(request, 'authentication/manage_permissions.html', {'permission': permission})


def profile(request):
    user = request.user  
    context = {
        'user': user,
    }
    return render(request, 'authentication/profile.html', context)

# views.py



#--------------------------department ------------------------

from .forms import DepartmentForm
from .models import Departments



import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from django.conf import settings
import os
from asset_App.utils import generate_dpt_qr_code


def create_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            # First save the department to get its ID
            department = form.save()
            
            # Generate URL for QR code
            dpt_url = request.build_absolute_uri(
                reverse('department_assets', args=[department.id])
            )
            
            # Generate QR code and update department
            department.qr_code_base64 = generate_dpt_qr_code(
                department.dpt_name, 
                dpt_url
            )
            department.save()
            
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'authentication/create_department.html', {'form': form})

def department_assets(request, department_id):
    department = get_object_or_404(Departments, id=department_id)
    assets = AssetData.objects.filter(department=department)
    
    # Assuming all assets are from the same office, take the first asset's office
    office_name = assets[0].office.name if assets.exists() else None
    office_address = assets[0].office.address if assets.exists() else None
    office_logo = assets[0].office.logo_image.url if assets.exists() and assets[0].office.logo_image else None

    return render(request, 'authentication/department_assets.html', {
        'department': department,
        'assets': assets,
        'office_name': office_name,
        'office_address': office_address,
        'office_logo': office_logo,
    })


from django.core.paginator import Paginator
def departmentList(request):
    search_query = request.GET.get('q', '')  # Default to an empty string if no search term is provided
    
    # Filter departments based on search query
    if search_query:
        departments = Departments.objects.filter(dpt_name__icontains=search_query)
    else:
        departments = Departments.objects.all()
    paginator = Paginator(departments, 10)  # Show 10 departments per page
    page_number = request.GET.get('page')  # Get the current page number from the GET request
    page_obj = paginator.get_page(page_number)  # Get the paginated page object
    
    # Add QR code for each department on the current page
    for dpt in page_obj:
        # Generate URL for QR code
        dpt_url = request.build_absolute_uri(
            reverse('department_assets', args=[dpt.id])
        )
        
        # Generate QR code in base64 and attach it to each department
        dpt.qr_code_base64 = generate_dpt_qr_code(dpt.dpt_name, dpt_url)
        dpt.save()

    # Prepare context with paginated data and the search query
    context = {
        'departments': page_obj,  # Paginated list of departments
        'search_query': search_query,  # Keep the search query in the template
    }
    
    return render(request, 'authentication/department_list.html', context)



from django.shortcuts import get_object_or_404

def edit_department(request, department_id):
    department = get_object_or_404(Departments, id=department_id)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')  # Redirect after editing
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'authentication/edit_department.html', {'form': form, 'department': department})
from django.http import JsonResponse

def delete_department(request, department_id):
    department = get_object_or_404(Departments, id=department_id)
    if request.method == "POST":
        department.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



def department_detail(request, department_id):
    department = get_object_or_404(Departments, id=department_id)
    assets = AssetData.objects.filter(department=department)  # Get all associated assets
    print('assets:',assets)
    return render(request, 'authentication/department_detail.html', {
        'department': department,
        'assets': assets,  # Pass the list of assets to the template
    })




from .forms import CommissionMembersForm  
from .models import ChairMan,CommissionMembers# Assuming you have created a ModelForm

# List all Commission Members
def commission_members_list(request):
    members = CommissionMembers.objects.all()
    return render(request, 'authentication/commission_members_list.html', {'members': members})



# Create a new Commission Member
def commission_member_create(request):
    if request.method == "POST":
        form = CommissionMembersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('commission_members_list')
    else:
        form = CommissionMembersForm()
    return render(request, 'authentication/commission_member_form.html', {'form': form})

def commission_member_edit(request, pk):
    member = get_object_or_404(CommissionMembers, pk=pk)
    if request.method == "POST":
        form = CommissionMembersForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Commission member updated successfully!')
            return redirect('commission_members_list')
    else:
        form = CommissionMembersForm(instance=member)
    return render(request, 'authentication/commission_member_form.html', {
        'form': form,
        'title': 'Edit Commission Member'
    })

def commission_member_delete(request, pk):
    if request.method == "POST":
        member = get_object_or_404(CommissionMembers, pk=pk)
        try:
            member.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from .models import ChairMan
from .forms import ChairManForm  # Assuming you have created a ModelForm

# List all ChairMan entries
def chairman_list(request):
    chairmen = ChairMan.objects.all()
    return render(request, 'authentication/chairman_list.html', {'chairmen': chairmen})



# Create a new ChairMan
def chairman_create(request):
    if request.method == "POST":
        form = ChairManForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chairman_list')
    else:
        form = ChairManForm()
    return render(request, 'authentication/chairman_form.html', {'form': form})



def chairman_edit(request, pk):
    chairman = get_object_or_404(ChairMan, pk=pk)
    if request.method == "POST":
        form = ChairManForm(request.POST, instance=chairman)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chairman updated successfully!')
            return redirect('chairman_list')
    else:
        form = ChairManForm(instance=chairman)
    return render(request, 'authentication/chairman_form.html', {
        'form': form,
        'title': 'Edit Chairman'
    })

def chairman_delete(request, pk):
    if request.method == "POST":
        chairman = get_object_or_404(ChairMan, pk=pk)
        try:
            chairman.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
# views.py

from .models import CommissionMembers
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET"])
def get_commission_members(request):
    try:
        # Replace this with your actual commission members model and query
        members = CommissionMembers.objects.all()
        members_data = [{'id': member.id, 'name': member.name} for member in members]
        return JsonResponse(members_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    

from django.utils import translation

def change_language(request, language_code):
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    if language_code in ['en', 'uz']:
        translation.activate(language_code)
        response.set_cookie('django_language', language_code)
    return response