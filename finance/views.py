from django.shortcuts import render,redirect,HttpResponse
from django.views import View
from finance.forms import RegisterForm,TransactionForm,GoalForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction,Goal
from django.db.models import Sum
from .admin import TransactionRescource
from django.contrib import messages

class RegsiterView(View):
    def get(self,request,*args, **kwargs):
        form = RegisterForm()
        return render(request,'finance/register.html',{'form':form})
    
    def post(self,request,*args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,'Account created successfully!')
            return redirect('dashboard')
        return render(request,'finance/register.html',{'form':form})
                
class DashboardView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        transactions = Transaction.objects.filter(user = request.user)
        goals = Goal.objects.filter(user = request.user)

        total_income = Transaction.objects.filter(user=request.user, transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Transaction.objects.filter(user=request.user, transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0


        net_saving = total_income - total_expense

        remaining_saving = net_saving

        goal_progress = []
        for goal in goals:
            if remaining_saving >= goal.target_amount:
                goal_progress.append({'goal':goal,'progress':100})
                remaining_saving -= goal.target_amount
            elif remaining_saving > 0:
                progress = (remaining_saving / goal.target_amount) * 100
                remaining_saving = 0
            else:
                goal_progress.append({'goal':goal,'progress':0})        

        context = {
            'transactions':transactions,
            'total_income':total_income,
            'total_expense':total_expense,
            'net_saving':net_saving,
            'goal_progress':goal_progress,
        }

        return render(request,'finance/dashboard.html',context)
    

class TraansactionCreateView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = TransactionForm(request.POST)
        return render(request,'finance/transaction_form.html',{'form':form})
    

    def post(self,request,*args, **kwargs):
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request,'Transaction added successfully!')
            return redirect('dashboard')
        return render(request,'finance/transaction_form.html',{'form':form})    



class TransactionListView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        transactions = Transaction.objects.filter(user = request.user)
        return render(request,'finance/transaction_list.html',{'transactions':transactions})
    


class GoalCreateView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = GoalForm(request.POST)
        return render(request,'finance/goal_add.html',{'form':form})
    

    def post(self,request,*args, **kwargs):
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request,'Goal created successfully!')
            return redirect('dashboard')
        return render(request,'finance/goal_add.html',{'form':form})  



def export_transactions(request):
    user_transaction = Transaction.objects.filter(user = request.user)
    transaction_resource = TransactionRescource()
    data_Set = transaction_resource.export(queryset=user_transaction)

    excel_data = data_Set.export('xlsx')

    response = HttpResponse(excel_data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 

    response['content-Disposition'] = 'attachment;filename=transactions_report.xlsx'

    return response