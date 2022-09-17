from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post
from django.utils import timezone


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    # posts 쿼리셋 객체를 post_list.html 템플릿에 전달
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        # 폼에서 입력된 데이터를 PostForm으로 넘겨주기.
        form = PostForm(request.POST)
        if form.is_valid(): # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
            post = form.save(commit=False) # 폼을 저장하지만, 바로 Post모델에 저장하지 않도록 commit옵션 False
            post.author = request.user # 작성자를 Post 모델에 추가
            post.published_date = timezone.now()
            post.save() # 새 Post 글 생성
            return redirect('post_detail', pk=post.pk) # 블로그 글을 작성한다음 post_detail페이지로 자동이동.
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
