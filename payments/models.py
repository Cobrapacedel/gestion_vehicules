from django.conf import settings
from django.db import models
from vehicles.models import Vehicle

class TollTransaction(models.Model):
    BTC = 'BTC'
    USDT = 'USDT TRC20'
    CURRECY_CHOICES = [
        (BTC, "Bitcoin (BTC)"),
        (USDT, "USDT TRC20"),
    ]
    
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_toll_transactions")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="vehicle_toll_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="BTC")
    status = models.CharField(max_length=20, default="pending")  # pending, completed, failed
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"

def update_status(self, new_status):
    if new_status in [self.PENDING, self.COMPLETED, self.FAILED]:
        self.status = new_status
        self.save()
