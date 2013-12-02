from news.models import NewsItem
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

def browse_news(request):
    news_list = NewsItem.objects.filter(visible=True).order_by('-time_published')
    
    # Split the result by 4
    paginator = Paginator(news_list, 4)
    
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        # Raise error because no more news is availble
        raise 
    
    if request.is_ajax():
        return render(request, 'includes/news_list.html', {'news': news})
        
    return render(request, 'news/browse_news.html', {'news': news})

def view_news(request, news_item_id):
    news_item = get_object_or_404(NewsItem, pk=news_item_id)
    
    return render(request, 'news/view_news.html', {'news_item': news_item})