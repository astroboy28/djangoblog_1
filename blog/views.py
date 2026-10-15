from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Category # Post/Category classes
from django.db import models # Django's models toolkit, needed for models.Q(...)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PostForm, RegisterForm


class MyPostsView(LoginRequiredMixin, ListView):
     model = Post
     template_name = "blog/my_posts.html"
     context_object_name = "page_obj"
     paginate_by = 6
     login_url = "login"

     def get_queryset(self):
         return Post.objects.filter(author=self.request.user).order_by("-created_at")

class RegisterView(CreateView):
     form_class = RegisterForm
     template_name = "blog/register.html"
     success_url = "/"

     def form_valid(self, form):
         response = super().form_valid(form)
         login(self.request, self.object)
         return response

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.get_object().author == self.request.user

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        qs = Post.objects.filter(status="published").select_related("category", "author").prefetch_related("tags").order_by("-created_at")
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__name__iexact=category_slug)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(title__icontains=query) | qs.filter(content__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        post = Post.objects.filter(status="published")
        if self.request.user.is_authenticated:
            post = Post.objects.filter(
                models.Q(status="published") | models.Q(author=self.request.user)
            )
        return post

def custom_403(request, exception=None):
    return render(request, "blog/403.html", status=403)

def about(request):
    return render(request, 'blog/about.html', {'content': 'This is the Djangoblog team.'})

def contact(request):
    return render(request, 'blog/contact.html', {'contact': 'This is the Contact Page.'})

