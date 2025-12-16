## lObjetivo

* Mostrar no Financeiro apenas dois totais:

  * Total virtual: valores pagos via PIX (dinheiro "virtual").

  * Total físico: valores pagos em dinheiro no balcão (dinheiro "por fora").

## Comportamento atual

* O total no painel financeiro soma por status do agendamento: pago/pendente/falhou (dashboard/views.py:66–81).

* Quando o cliente escolhe PIX e paga, o status vai para "pago" (payments/views.py:76–94) e aparece como "Pix" nas telas (dashboard/templates/dashboard/admin\_finance.html:39; payments/templates/payments/sucesso.html:31).

* Quando o cliente escolhe "Pagar na hora", o status fica "pendente" e não há registro explícito de pagamento em dinheiro (payments/views.py:50–63). Isso impede calcular um total realmente "pago" em dinheiro.

## Proposta de design

1. Introduzir o método de pagamento no agendamento:

   * Adicionar campo `payment_method` em `Appointment` com choices: `pix` e `cash`.

   * Persistir o método selecionado no fluxo:

     * Ao iniciar/confirmar PIX: `payment_method = 'pix'`.

     * Ao escolher "Pagar na hora": `payment_method = 'cash'`.
2. Separar o conceito de método (como o cliente vai pagar) do status (se já pagou ou não):

   * `payment_status` continua: `pendente`, `pago`, `falhou` (scheduling/models.py:13–17,24).

   * Regra de negócio para totais:

     * Total virtual = soma de `price()` dos agendamentos com `payment_status='pago'` e `payment_method='pix'`.

     * Total físico = soma de `price()` dos agendamentos com `payment_status='pago'` e `payment_method='cash'`.
3. Adicionar no painel/admin uma ação simples para confirmar pagamento em dinheiro:

   * Botão/endpoint para marcar um agendamento com `payment_method='cash'` como `payment_status='pago'` quando o cliente pagar no balcão.

## Alterações de implementação

* Modelos:

  * `scheduling/models.py`: adicionar `payment_method = models.CharField(choices=[('pix','Pix'),('cash','Dinheiro')], default='cash', max_length=10)`.

* Views de pagamento:

  * `payments/views.py`:

    * Em `pagamento_confirmar(...)`: definir `ap.payment_method='pix'` quando gerar o QR.

    * Em `pagamento_check(...)`: manter `ap.payment_status='pago'` (já existe) e garantir `payment_method='pix'`.

    * Em `pagamento_na_hora(...)`: definir `ap.payment_method='cash'` (status permanece `pendente`).

* Painel Financeiro:

  * `dashboard/views.py::admin_finance(...)`: calcular apenas dois totais:

    * `total_virtual`: pagos com método `pix`.

    * `total_fisico`: pagos com método `cash`.

  * Lista de pagos pode continuar mostrando apenas os pagos, mas a coluna "Forma de pagamento" deve usar o novo campo.

* Templates:

  * `dashboard/templates/dashboard/admin_finance.html`:

    * Substituir os três cards por dois: "Total virtual (PIX)" e "Total físico (dinheiro)".

    * Na tabela, usar `ap.payment_method` para exibir "Pix" ou "Dinheiro".

  * `payments/templates/payments/pagamento.html`:

    * Em "Forma de pagamento", usar `payment_method` para indicar a escolha atual.

  * `payments/templates/payments/sucesso.html`:

    * Exibir "Pix" ou "Dinheiro" com base em `payment_method`.

* Ação/Admin para confirmar dinheiro:

  * Endpoint simples em `dashboard/views.py` (ex.: `admin_mark_cash_paid(appointment_id)`), que muda `payment_status` para `pago` quando receber no balcão.

## Migração de dados

* Criar migração para adicionar o campo `payment_method` com default `cash`.

* Backfill dos registros existentes:

  * Se `payment_status='pago'` e houve fluxo PIX, marcar `payment_method='pix'`.

  * Caso contrário, manter `cash`. (Os valores em dinheiro só contarão no total físico quando forem marcados como `pago`).

## Validação

* Testar cenários:

  * PIX: gerar QR, confirmar, ver `total_virtual` subir e método exibido como "Pix".

  * Dinheiro: escolher "na hora", marcar como pago no painel, ver `total_fisico` subir e método exibido como "Dinheiro".

* Conferir no `admin_finance` que apenas dois cards aparecem e somas batem com os agendamentos e seus preços (combo=100, outros=50).

## Observações

* Mantemos a lógica dos preços em `Appointment.price()` (scheduling/models.py:31–35).

* Não alteramos o fluxo de PIX; apenas registramos o método e separamos as somas por método.

* A confirmação manual em dinheiro dá controle ao barbeiro/gerente e evita contar valores pendentes como pagos.

Se aprovar, implemento as mudanças, migração e ajuste das telas em seguida.
