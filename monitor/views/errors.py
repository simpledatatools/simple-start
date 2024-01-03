from django.shortcuts import render

def error_403(request, exception):
        data = {}
        return render(request,'monitor/errors/403.html', status=403)

def error_404(request, exception):
        data = {}
        return render(request,'monitor/errors/404.html', status=404)

def error_500(request):
        return render(request,'monitor/errors/500.html', status=500)