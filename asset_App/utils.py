# import qrcode
# from django.conf import settings
# import base64
# from io import BytesIO
# import os



# def generate_qr_code(asset_name, url):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(url)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")
    
#     qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f'{asset_name}.png')
#     os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)
#     img.save(qr_code_path)
    
#     return f'{settings.MEDIA_URL}qr_codes/{asset_name}.png'


import qrcode
import base64
from io import BytesIO

# def generate_qr_code(asset_name, url):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(url)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")

#     buffered = BytesIO()
#     img.save(buffered, format="PNG")
#     img_str = base64.b64encode(buffered.getvalue()).decode()
    
#     return f'data:image/png;base64,{img_str}'


import os
from io import BytesIO
import qrcode
from django.conf import settings

import qrcode
import os
from django.conf import settings

def generate_qr_code(asset_name, url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to the media directory
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)  # Create directory if it doesn't exist
    qr_code_path = os.path.join(qr_code_dir, f'{asset_name}.png')
    img.save(qr_code_path)

    # Return the URL to the saved QR code image
    return os.path.join(settings.MEDIA_URL, 'qr_codes', f'{asset_name}.png')



import os
import re
import qrcode
from django.conf import settings

def generate_dpt_qr_code(dpt_name, url):
    # Sanitize department name to ensure it’s a valid filename
    sanitized_name = re.sub(r'\W+', '_', dpt_name)  # Replace non-alphanumeric characters with underscores
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to the media directory
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'dpt_qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Use the sanitized department name for the filename
    qr_code_path = os.path.join(qr_code_dir, f'{sanitized_name}.png')
    img.save(qr_code_path)

    # Return the URL to the saved QR code image
    return os.path.join(settings.MEDIA_URL, 'dpt_qr_codes', f'{sanitized_name}.png')

# utils.py
import pandas as pd
from .models import AssetType, HeadOffice, Branches, Departments, AssetData, AssetImage, AssetBill
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

def process_excel_file(excel_file):
    df = pd.read_excel(excel_file)
    
    for _, row in df.iterrows():
        try:
            # Get or create related objects
            asset_type = AssetType.objects.get(name=row['asset_type'])
            office = HeadOffice.objects.get(name=row['office'])
            branch = Branches.objects.get(branch_name=row['branch'])
            department = Departments.objects.get(dpt_name=row['department'])

            # Create AssetData instance
            asset = AssetData.objects.create(
                asset_type=asset_type,
                asset_code=row['asset_code'],
                office=office,
                branch=branch,
                department=department,
                asset_name=row['asset_name'],
                model=row['model'],
                serial_number=row['serial_number'],
                purchase_date=row['purchase_date'],
                warranty_info=row['warranty_info'],
                price=row['price'],
                is_sold=row['is_sold']
            )

            # Process images
            image_paths = row['image_paths'].split(',') if pd.notna(row['image_paths']) else []
            for path in image_paths:
                with open(path.strip(), 'rb') as img_file:
                    AssetImage.objects.create(asset=asset, image=File(img_file))

            # Process bills
            bill_paths = row['bill_file_paths'].split(',') if pd.notna(row['bill_file_paths']) else []
            for path in bill_paths:
                with open(path.strip(), 'rb') as bill_file:
                    AssetBill.objects.create(asset=asset, bill_file=File(bill_file))

        except ObjectDoesNotExist as e:
            raise Exception(f"Error processing row {_+2}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing row {_+2}: {str(e)}")
        
        


from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

def get_asset_statistics(queryset):
    """Calculate various asset statistics"""
    stats = {
        'total_count': queryset.count(),
        'total_value': queryset.aggregate(Sum('price'))['price__sum'] or 0,
        'active_count': queryset.filter(is_sold=False).count(),
        'sold_count': queryset.filter(is_sold=True).count(),
        'avg_age': queryset.exclude(purchase_date=None).aggregate(
            avg_age=Avg((datetime.now().date() - F('purchase_date')).days / 365)
        )['avg_age'] or 0
    }
    return stats

def get_monthly_acquisitions(queryset, months=12):
    """Get asset acquisition data for the last n months"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)
    
    monthly_data = queryset.filter(
        purchase_date__gte=start_date
    ).annotate(
        month=TruncMonth('purchase_date')
    ).values('month').annotate(
        count=Count('id'),
        value=Sum('price')
    ).order_by('month')
    
    return monthly_data

def calculate_depreciation_summary(queryset):
    """Calculate depreciation summary for assets"""
    summary = {
        'fully_depreciated': 0,
        'active': 0,
        'total_depreciation': 0
    }
    
    for asset in queryset:
        current_value = asset.get_current_value()
        if current_value <= 0:
            summary['fully_depreciated'] += 1
        else:
            summary['active'] += 1
        summary['total_depreciation'] += float(asset.price) - current_value
    
    return summary