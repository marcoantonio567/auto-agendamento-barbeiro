from django.db import models
from django.conf import settings
from core.models import BaseModel
from payments.constans import PAYMENT_METHOD, PAYMENT_STATUS

class Payment(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        db_column='id_usuario'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Valor'
    )

    payment_method = models.CharField(
        choices=PAYMENT_METHOD,
        verbose_name='Método de pagamento',
        db_column='metodo_pagamento'
    )
    status = models.CharField(
        choices=PAYMENT_STATUS,
        verbose_name='Status',
        db_column='status'
    )   

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        db_table = 'tb_pagamento'

    def __str__(self):
        return f'{self.user} - {self.payment_method} - {self.status}'
  
