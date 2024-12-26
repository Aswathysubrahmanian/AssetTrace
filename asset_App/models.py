
from django.db.models import JSONField
from django.db import models
from authentication.models import HeadOffice,Branches,Departments
from decimal import Decimal
import datetime
from django.utils import timezone



class AssetType(models.Model):
    name = models.CharField(max_length=200,unique=True)
    office = models.ForeignKey(HeadOffice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class AssetData(models.Model):
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assets')
    asset_code=models.CharField(max_length=200,unique=True)
    office=models.ForeignKey(HeadOffice,on_delete=models.CASCADE)
    branch=models.ForeignKey(Branches,on_delete=models.CASCADE)
    department=models.ForeignKey(Departments,on_delete=models.CASCADE)
    asset_name = models.CharField(max_length=200)
    model = models.CharField(max_length=200,null=True,blank=True)
    serial_number = models.CharField(max_length=200, unique=True,null=True,blank=True)
    purchase_date = models.DateField(null=True,blank=True)
    warranty_info = models.CharField(max_length=200,null=True,blank=True)
    price = models.DecimalField(max_digits=30, decimal_places=5)
    is_sold = models.BooleanField(default=False)
    custodian=models.CharField(max_length=30,null=True,blank=True)
    sold_date = models.DateField(null=True, blank=True)  # New field to track sold date
    verified=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically set sold_date when asset is marked as sold
        if self.is_sold and not self.sold_date:
            self.sold_date = timezone.now().date()  # Set the current date
        elif not self.is_sold:
            self.sold_date = None  # Reset sold_date if not sold anymore
        super().save(*args, **kwargs)
        
    def mark_as_verified(self):
        self.verified = True
        self.save()

    def mark_as_unverified(self):
        self.verified = False
        self.save()
        
    @property
    def price_in_usd(self):
        # You can store the exchange rate in settings or fetch it from an API
        UZS_TO_USD_RATE = Decimal('0.000082')  # Example rate: 1 UZS = 0.000082 USD
        return round(self.price * UZS_TO_USD_RATE, 2)
    
    
    
    def generate_asset_code(self):
        prefix = self.branch.prefix  # Assuming branch has a prefix field
        last_asset = AssetData.objects.filter(
            branch=self.branch,
            asset_code__startswith=f"{prefix}-"
        ).order_by('-asset_code').first()

        if last_asset:
            try:
                last_number = int(last_asset.asset_code.split('-')[-1])
                new_number = str(last_number + 1).zfill(3)
            except ValueError:
                new_number = '001'
        else:
            new_number = '001'

        return f"{prefix}-{new_number}"
    

    def __str__(self) -> str:
        return self.asset_name

    def get_current_value(self):
        """Calculate current value after depreciation"""
        depreciation = self.depreciations.first()
        if depreciation and self.purchase_date:
            years_owned = (datetime.now().date() - self.purchase_date).days / 365
            depreciation_schedule = depreciation.calculate_depreciation()
            current_value = float(self.price)
            for year, amount in depreciation_schedule:
                if year <= years_owned:
                    current_value -= amount
            return max(current_value, 0)
        return self.price

    def get_age(self):
        """Calculate asset age in years"""
        if self.purchase_date:
            days = (datetime.now().date() - self.purchase_date).days
            return round(days / 365, 1)
        return 0

    def get_depreciation_status(self):
        """Get depreciation status"""
        current_value = self.get_current_value()
        if current_value <= 0:
            return "Fully Depreciated"
        elif current_value < float(self.price) * 0.2:
            return "Nearly Depreciated"
        else:
            return "Active"

    class Meta:
        ordering = ['-purchase_date']

class CustomField(models.Model):
    asset = models.ForeignKey(AssetData, related_name='custom_fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_value = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return f'{self.field_name} for {self.asset}'
    
#---------------------------------------------------------------------------------------------------------------------------------------------  
    
    

class Depreciation(models.Model):
    DEPRECIATION_METHODS = [
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
        ('sum_of_years_digits', 'Sum of the Years Digits'),
        ('other', 'Other'),
    ]
    asset = models.ForeignKey(AssetData, related_name='depreciations', on_delete=models.CASCADE)
    branch=models.ForeignKey(Branches,on_delete=models.CASCADE,null=True,blank=True)
    office=models.ForeignKey(HeadOffice,on_delete=models.CASCADE,null=True,blank=True)
    purchase_value = models.DecimalField(max_digits=30, decimal_places=10)
    useful_life = models.PositiveIntegerField()
    depreciation_method = models.CharField(max_length=20, choices=DEPRECIATION_METHODS)
    salvage_value = models.DecimalField(max_digits=30, decimal_places=10, null=True, blank=True)
    custom_percentages = models.JSONField(null=True, blank=True)
    is_custom = models.BooleanField(default=False,null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set these values when creating a new object
            self.branch = self.asset.branch
            self.office = self.asset.office
            
        super().save(*args, **kwargs)

    def calculate_depreciation(self):
        if self.depreciation_method == 'straight_line':
            return self._straight_line_depreciation()
        elif self.depreciation_method == 'declining_balance':
            return self._declining_balance_depreciation()
        elif self.depreciation_method == 'sum_of_years_digits':
            return self._sum_of_years_digits_depreciation()
        elif self.depreciation_method == 'other':
            return self._other_depreciation()
        return []

    def _straight_line_depreciation(self):
        purchase_value = Decimal(self.purchase_value)
        salvage_value = Decimal(self.salvage_value or 0)  # handle null salvage value
        useful_life = Decimal(self.useful_life)
        
        annual_depreciation = (purchase_value - salvage_value) / useful_life
        return [(year, float(annual_depreciation)) for year in range(1, self.useful_life + 1)]

    def _declining_balance_depreciation(self):
        purchase_value = Decimal(self.purchase_value)
        salvage_value = Decimal(self.salvage_value or 0)  # handle null salvage value
        useful_life = Decimal(self.useful_life)
        
        rate = Decimal(1) - (salvage_value / purchase_value) ** (Decimal(1) / useful_life)
        value = purchase_value
        depreciations = []
        for year in range(1, self.useful_life + 1):
            depreciation = value * rate
            value -= depreciation
            depreciations.append((year, float(depreciation)))
        return depreciations

    def _sum_of_years_digits_depreciation(self):
        purchase_value = Decimal(self.purchase_value)
        salvage_value = Decimal(self.salvage_value or 0)  # handle null salvage value
        useful_life = Decimal(self.useful_life)
        
        sum_of_years = sum(range(1, int(useful_life) + 1))
        depreciations = []
        for year in range(1, self.useful_life + 1):
            depreciation = (purchase_value - salvage_value) * (useful_life - Decimal(year) + Decimal(1)) / Decimal(sum_of_years)
            depreciations.append((year, float(depreciation)))
        return depreciations

    def _other_depreciation(self):
        if not self.custom_percentages:
            return []
        
        purchase_value = Decimal(self.purchase_value)
        value = purchase_value
        depreciations = []
        for year_percentage in self.custom_percentages:
            year = year_percentage.get('year')
            percentage = year_percentage.get('percentage')
            if year is None or percentage is None:
                continue
            depreciation = value * (Decimal(str(percentage)) / Decimal('100'))
            value -= depreciation
            depreciations.append((year, float(depreciation)))
        return depreciations
    
#------------------------------------------------------------------------------------------------------------------------------------------    

class AssetImage(models.Model):
    asset = models.ForeignKey(AssetData, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images')
   

    def __str__(self):
        return f"Image for {self.asset.asset_name}"

class AssetBill(models.Model):
    asset = models.ForeignKey(AssetData, on_delete=models.CASCADE, related_name='bills')
    bill_file = models.FileField(upload_to='asset_bills',null=True,blank=True)

    def __str__(self):
        return f"Bill for {self.asset.asset_name}"


#--------------------------------------------------------------------------------------------------------------------------------------------

class Asset_movement_data(models.Model):
    movement_choice = [
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary')
    ]
    
    asset = models.ForeignKey(AssetData, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=movement_choice)
    from_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='movements_from')
    to_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='movements_to')
    movement_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)  # For temporary movements

    def __str__(self):
        return f"{self.asset.asset_name} moved from {self.from_branch.branch_name} to {self.to_branch.branch_name} ({self.status})"
    

    class Meta:
        verbose_name_plural = 'Asset Movement'
        
    @staticmethod
    def get_current_branch(asset):
        latest_movement = Asset_movement_data.objects.filter(asset=asset).order_by('-movement_date').first()
        if latest_movement:
            return latest_movement.to_branch
        return asset.branch 
        


