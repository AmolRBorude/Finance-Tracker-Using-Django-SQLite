from django.urls import path
from finance.views import RegsiterView,DashboardView,TraansactionCreateView,TransactionListView,GoalCreateView,export_transactions

urlpatterns = [
    path('register/',RegsiterView.as_view(),name="register"),
    path('',DashboardView.as_view(),name="dashboard"),
    path('',DashboardView.as_view(),name="dashboard"),
    path('transaction/add',TraansactionCreateView.as_view(),name="transaction_add"),
    path('transactions/',TransactionListView.as_view(),name="transaction_list"),
    path('goal/add',GoalCreateView.as_view(),name="goal_add"),
    path('generate-report/',export_transactions,name="export_transactions"),
]
