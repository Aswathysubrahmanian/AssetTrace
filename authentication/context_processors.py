def user_role(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser:
            role = 'master'
        elif user.is_superadmin:
            role = 'super_admin'
        elif user.is_admin:
            role = 'admin'
        else:
            role = 'unknown'
    else:
        role = 'guest'
    return {'user_role': role}

def logo_context(request):
    if not request.user.is_authenticated:
        return {}
        
    user = request.user
    
    if user.head_office and user.head_office.logo_image:
        logo_url = user.head_office.logo_image.url
    elif user.branch and user.branch.logo_image:
        logo_url = user.branch.logo_image.url
    else:
        logo_url = None
        
    return {
        'logo_url': logo_url,
        
    }