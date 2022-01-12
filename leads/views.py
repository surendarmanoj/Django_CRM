from django.core.mail import send_mail
from django.db.models.query import InstanceCheckMeta, QuerySet
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.views import generic
from .models import Category, Lead, Agent
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, User, LeadCategoryUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganisorAndLoginRequiredMixin


#CRUD - Create, Retrieve, Update, Delete + List 
class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    def get_success_url(self):
        return reverse("login")


class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'

def landing_page(request):
    return render (request, "landing.html")

class loadlistView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_card_view.html"
    context_object_name = "leads"

    def get_queryset(self):
        user =self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation, agent__isnull=False)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        
        context = super(loadlistView, self).get_context_data(**kwargs)
        user =self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile, 
            agent__isnull=True)

            context.update({
                "unassigned_leads":queryset
            })
        return context

def card_view(request):
    leads = Lead.objects.all()
    context = {
       
        "leads" : leads
    }
    return render (request,"leads/lead_card_view.html", context)


def lead_list(request):
    leads = Lead.objects.all()
    context = {
       
        "leads" : leads
    }
    return render(request, "leads/leads_page.html", context)

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead":lead
    }
    return render(request, "leads/lead_detail.html", context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user =self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset


def lead_create(request):
    form = LeadModelForm()
    if request.method == 'POST':
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        'form':form
    }
    return render(request,"leads/lead_create.html", context)


class lead_create_view(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        #  TODO send email
        send_mail(
            subject="New lead",
            message="New lead has been created on the CRM",
            from_email="happystudentmemories@gmail.com",
            recipient_list=["surendarmanoj85@gmail.com"],
        )
        return super(lead_create_view, self).form_valid(form)
    

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == 'POST':
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
           form.save()
           return redirect("/leads")
    context = {
        'form':form,
        'lead': lead
    }
    return render(request, "leads/lead_update.html", context)

class lead_update_view(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user =self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
       

    def get_success_url(self):
        return reverse("leads:lead-list")

def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")

class lead_delete_view(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    def get_queryset(self):
        user =self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
    
    def get_success_url(self):
        return reverse("leads:lead-list")


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request":self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class categoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"


    def get_context_data(self, **kwargs):
        context = super(categoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset=Lead.objects.filter(
                organisation = user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation = user.agent.organisation
            )
        
        context.update({
            "unassigned_lead_count":queryset.filter(category__isnull=True).count()
            
        })
        return context

    def get_queryset(self):
        user =self.request.user

        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile, 
                
                )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
                )
            
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)

        # qs = Lead.objects.filter(category=self.get_object())
        leads = self.get_object().leads.all()
        
        context.update({
            "leads":leads
        })
        return context

    def get_queryset(self):
        user =self.request.user

        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile, 
                
                )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
                )
            
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation)
            queryset = queryset.filter(agent__user = user)

        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})





# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == 'POST':
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             return redirect("/leads")
#     context = {
#         'form':form,
#         'lead': lead
#     }
#     return render(request, "leads/lead_update.html", context)


# def lead_create(request):
    # form = LeadModelForm()
    # if request.method == 'POST':
    #     form = LeadModelForm(request.POST)
    #     if form.is_valid():
    #         print(form.cleaned_data)
    #         first_name = form.cleaned_data['first_name']
    #         last_name = form.cleaned_data['last_name']
    #         age = form.cleaned_data['age']
    #         agent = Agent.objects.first()
    #         Lead.objects.create(
    #             first_name = first_name,
    #             last_name = last_name,
    #             age = age,
    #             agent = agent
    #         )
    #         print("Lead has been created")
    #         return redirect("/leads")
    # context = {
    #     'form':form
    # }
#     return render(request,"leads/lead_create.html", context)
